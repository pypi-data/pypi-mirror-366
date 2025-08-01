"""
A2A OpenAI Agents Library

Provides a robust and elegant way to integrate OpenAI Agents (built with the `openai-agents` SDK)
with the A2A (Agent2Agent) Protocol.
"""

import asyncio
import re
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

try:
    import uvicorn
    from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication
    from a2a.server.request_handlers.jsonrpc_handler import JSONRPCHandler
    from a2a.types import AgentCapabilities, AgentCard, AgentSkill, Message, Part, Task, TaskStatus
    from agents import Agent, Runner
except ImportError as e:
    raise ImportError(
        f"Required dependencies not installed: {e}. "
        "Please install with: pip install a2a-openai-agents[all]"
    ) from e


class A2ASkillConfig:
    """Configuration for an A2A skill definition."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable[["A2AWrapper", dict[str, Any]], Awaitable[dict[str, Any] | Task]],
        parameters: dict[str, Any] | None = None,
    ):
        """
        Initialize an A2A skill configuration.

        Args:
            name: The public name of the A2A skill
            description: A human-readable description of the skill
            handler: An async callable that handles the skill execution
            parameters: JSON Schema for the skill's input parameters
        """
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters or {}


class A2AWrapper:
    """
    Main class for wrapping an agents.Agent instance to expose it as an A2A service.

    This class provides composition-based integration, taking an Agent instance as the "brain"
    and adding A2A interoperability around it.
    """

    def __init__(
        self,
        openai_agent: Agent,
        a2a_name: str | None = None,
        a2a_description: str | None = None,
        a2a_version: str = "1.0.0",
        a2a_id: str | None = None,
        a2a_skills: list[A2ASkillConfig] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the A2A wrapper around an OpenAI Agent.

        Args:
            openai_agent: The instance of the openai-agents Agent (required)
            a2a_name: Public name for the A2A Agent Card (defaults to openai_agent.name)
            a2a_description: Public description for the A2A Agent Card
            a2a_version: Version for the A2A Agent Card (default "1.0.0")
            a2a_id: Unique ID for the A2A Agent Card (defaults to slugified a2a_name)
            a2a_skills: List of A2ASkillConfig objects (auto-derived if None)
            **kwargs: Additional arguments for future extensions
        """
        self._openai_agent = openai_agent

        # Derive A2A metadata from openai_agent if not provided
        self._a2a_name = a2a_name or openai_agent.name or "A2AAgent"
        self._a2a_description = a2a_description or f"A2A wrapper for {self._a2a_name}"
        self._a2a_version = a2a_version
        self._a2a_id = a2a_id or self._slugify(self._a2a_name)

        # Internal task storage for durable operations
        self._tasks: dict[str, Task] = {}

        # Set or derive skills first
        self._a2a_skills = a2a_skills
        if self._a2a_skills is None:
            self._a2a_skills = self._derive_skills_from_tools()

        # Create agent card with all required fields
        self._agent_card = AgentCard(
            name=self._a2a_name,
            description=self._a2a_description,
            version=self._a2a_version,
            url="http://localhost:8000",  # Default URL, can be overridden
            capabilities=AgentCapabilities(),  # Default capabilities
            default_input_modes=["text"],  # Support text input by default
            default_output_modes=["text"],  # Support text output by default
            skills=self._convert_skills_to_agent_skills(),  # Convert our skills
        )

        # Create the A2A application (will be created when needed)
        self._app = None

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to a URL-safe slug."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _derive_skills_from_tools(self) -> list[A2ASkillConfig]:
        """Automatically derive A2A skills from the OpenAI agent's tools."""
        skills: list[A2ASkillConfig] = []

        if not hasattr(self._openai_agent, "tools") or not self._openai_agent.tools:
            return skills

        for tool in self._openai_agent.tools:
            # Handle FunctionTool directly (agents package structure)
            if hasattr(tool, "name") and hasattr(tool, "params_json_schema"):
                skill_name = tool.name
                skill_description = tool.description or f"Execute {skill_name}"

                # Extract parameters from the tool's JSON schema
                parameters = getattr(tool, "params_json_schema", {})

                # Create a handler that delegates to the wrapped agent
                def create_handler(tool_name: str):
                    async def handler(
                        wrapper_instance: "A2AWrapper", params: dict[str, Any]
                    ) -> dict[str, Any]:
                        # Craft a prompt for the agent to use this specific tool
                        prompt = f"Use the {tool_name} tool with these parameters: {params}"
                        result = await wrapper_instance.process_prompt_with_internal_agent(prompt)
                        return {"result": result}

                    return handler

                skill = A2ASkillConfig(
                    name=skill_name,
                    description=skill_description,
                    handler=create_handler(skill_name),
                    parameters=parameters,
                )
                skills.append(skill)

        return skills

    def _convert_skills_to_agent_skills(self) -> list[AgentSkill]:
        """Convert A2ASkillConfig objects to AgentSkill objects for the agent card."""
        agent_skills = []

        for skill in self._a2a_skills:
            agent_skill = AgentSkill(
                id=self._slugify(skill.name),  # Use slugified name as ID
                name=skill.name,
                description=skill.description,
                parameters=skill.parameters,
                tags=[],  # Empty tags for now
            )
            agent_skills.append(agent_skill)

        return agent_skills

    def get_app(self):
        """Get the FastAPI application for this A2A wrapper."""
        if self._app is None:
            # Create a custom request handler for our agent
            request_handler = self._create_request_handler()

            # Create the A2A FastAPI application
            self._app = A2AFastAPIApplication(
                agent_card=self._agent_card,
                http_handler=JSONRPCHandler(
                    agent_card=self._agent_card,
                    request_handler=request_handler,
                ),
            )

        return self._app

    def _create_request_handler(self):
        """Create a custom request handler that implements the A2A protocol."""
        from a2a.server.context import ServerCallContext
        from a2a.server.request_handlers.request_handler import RequestHandler
        from a2a.types import TaskQueryParams

        class AgentRequestHandler(RequestHandler):
            def __init__(self, wrapper):
                self.wrapper = wrapper

            async def on_get_task(
                self, params: TaskQueryParams, context: ServerCallContext | None = None
            ) -> Task | None:
                """Handle get task requests."""
                return self.wrapper._tasks.get(params.task_id)

            async def on_message_send(
                self, params, context: ServerCallContext | None = None
            ) -> Task:
                """Handle send message requests."""
                return await self.wrapper._process_message(params)

            async def on_message_send_stream(
                self, params, context: ServerCallContext | None = None
            ):
                """Handle streaming message requests."""
                # For now, just call the regular message send
                task = await self.on_message_send(params, context)
                yield task

            async def on_cancel_task(
                self, params, context: ServerCallContext | None = None
            ) -> Task | None:
                """Handle task cancellation requests."""
                # Basic implementation - mark task as cancelled if it exists
                task = self.wrapper._tasks.get(params.task_id)
                if task:
                    setattr(task, 'status', TaskStatus(
                        state="canceled", message=None
                    ))
                return task

            async def on_resubscribe_to_task(
                self, params, context: ServerCallContext | None = None
            ) -> Task | None:
                """Handle task resubscription requests."""
                return self.wrapper._tasks.get(params.task_id)

            # Push notification methods (basic no-op implementations)
            async def on_get_task_push_notification_config(
                self, params, context: ServerCallContext | None = None
            ):
                """Get push notification config."""
                return None

            async def on_set_task_push_notification_config(
                self, params, context: ServerCallContext | None = None
            ):
                """Set push notification config."""
                return None

            async def on_delete_task_push_notification_config(
                self, params, context: ServerCallContext | None = None
            ):
                """Delete push notification config."""
                return None

            async def on_list_task_push_notification_config(
                self, params, context: ServerCallContext | None = None
            ):
                """List push notification configs."""
                return []

        return AgentRequestHandler(self)

    async def _process_message(self, params) -> Task:
        """Process an incoming message with the OpenAI agent."""
        # Extract message content from A2A protocol format
        message = getattr(params, "message", None)
        text_content = ""

        if message:
            # Process the single message
            for part in getattr(message, "parts", []):
                if getattr(part, "type", "") == "text":
                    text_content += getattr(part, "text", "") + " "

        if not text_content.strip():
            # Return error task if no text content found
            task_id = f"task-{uuid.uuid4()}"
            context_id = f"ctx-{uuid.uuid4()}"
            error_task = Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state="failed", message=None),
            )
            self._tasks[task_id] = error_task
            return error_task

        try:
            # Process with the internal agent
            result = await self.process_prompt_with_internal_agent(text_content.strip())

            # Create response task
            task_id = f"task-{uuid.uuid4()}"
            context_id = f"ctx-{uuid.uuid4()}"
            response_message = Message(
                message_id=f"msg-{uuid.uuid4()}",
                role="assistant",
                parts=[Part(type="text", text=result)]
            )
            response_task = Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state="completed", message=None),
                history=[response_message],
            )

            # Store the task
            self._tasks[task_id] = response_task
            return response_task

        except (RuntimeError, ValueError, TypeError) as e:
            # Return error task on failure
            task_id = f"task-{uuid.uuid4()}"
            context_id = f"ctx-{uuid.uuid4()}"
            error_task = Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state="failed", message=None),
            )
            self._tasks[task_id] = error_task
            return error_task

    async def process_prompt_with_internal_agent(self, prompt: str) -> str:
        """
        Process a prompt using the wrapped OpenAI agent.

        Args:
            prompt: The prompt string to process

        Returns:
            The final output from the agent's run
        """
        runner = Runner(self._openai_agent)
        run_result = await asyncio.get_event_loop().run_in_executor(None, runner.run, prompt)
        return run_result.final_output

    @property
    def a2a_skills(self) -> list[A2ASkillConfig]:
        """Get the current list of A2A skills."""
        return self._a2a_skills or []

    @a2a_skills.setter
    def a2a_skills(self, skills: list[A2ASkillConfig]):
        """Set/override the list of A2A skills."""
        self._a2a_skills = skills
        # Update agent card with new skills
        setattr(self._agent_card, 'skills', self._convert_skills_to_agent_skills())
        # Reset the app so it gets recreated with new skills
        self._app = None

    async def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID from internal storage."""
        return self._tasks.get(task_id)

    async def handle_a2a_task_update(
        self, task_id: str, status: str, message: str = "", result: dict[str, Any] | None = None
    ) -> None:
        """
        Update the internal state of a tracked A2A Task.

        This method is designed to be called by external services (e.g., Temporal workflows)
        to update task status.

        Args:
            task_id: The ID of the task to update
            status: The new status (working, completed, failed, etc.)
            message: Status message (currently not used by A2A TaskStatus)
            result: Optional result data for completed tasks
        """
        if task_id in self._tasks:
            task = self._tasks[task_id]
            # A2A TaskStatus expects message to be None or a Message object, not string
            setattr(task, 'status', TaskStatus(state=status, message=None))
            # Note: A2A Task doesn't have a result field, results are in metadata or history


def run_a2a_wrapper_server(
    wrapper_instance: A2AWrapper, port: int = 8000, host: str = "0.0.0.0"
) -> None:
    """
    Convenience function to start the A2A HTTP server for an A2AWrapper instance.

    Args:
        wrapper_instance: The A2AWrapper instance to serve
        port: The port to run the server on (default 8000)
        host: The host address to bind to (default "0.0.0.0")
    """
    # Get the A2AFastAPIApplication from the wrapper
    a2a_app = wrapper_instance.get_app()

    # Build the actual FastAPI app that uvicorn can serve
    fastapi_app = a2a_app.build()

    # Run with uvicorn
    uvicorn.run(fastapi_app, host=host, port=port)


def main():
    """Entry point for the CLI command."""
    print("a2a-openai-agents library")
    print("Use this library to wrap OpenAI agents with A2A protocol support.")


if __name__ == "__main__":
    main()
