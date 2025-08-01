"""Integration tests for A2A functionality."""

import pytest
from unittest.mock import Mock, patch
import asyncio

from a2a_openai_agents import A2AWrapper, A2ASkillConfig


class TestIntegration:
    """Integration tests for complete A2A workflows."""

    def test_end_to_end_wrapper_creation(self):
        """Test complete A2AWrapper creation and configuration."""
        # Create a mock agent with tools
        mock_tool = Mock()
        mock_tool.name = "test_function"
        mock_tool.description = "Test function description"
        mock_tool.params_json_schema = {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Test parameter"}
            },
            "required": ["param1"]
        }

        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = [mock_tool]

        # Create wrapper
        wrapper = A2AWrapper(
            openai_agent=mock_agent,
            a2a_description="Integration test agent"
        )

        # Verify complete setup
        assert wrapper._a2a_name == "TestAgent"
        assert wrapper._a2a_description == "Integration test agent"
        assert len(wrapper.a2a_skills) == 1
        assert wrapper.a2a_skills[0].name == "test_function"

        # Verify agent card
        agent_card = wrapper._agent_card
        assert agent_card.name == "TestAgent"
        assert agent_card.description == "Integration test agent"
        assert len(agent_card.skills) == 1
        assert agent_card.skills[0].name == "test_function"

        # Verify app creation
        app = wrapper.get_app()
        assert app is not None

    @pytest.mark.asyncio
    async def test_custom_skill_execution(self):
        """Test execution of custom skills."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        # Create a custom skill
        async def test_skill_handler(wrapper_instance, params):
            name = params.get("name", "World")
            return {"greeting": f"Hello, {name}!"}

        custom_skill = A2ASkillConfig(
            name="greet",
            description="Greet someone",
            handler=test_skill_handler,
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to greet"}
                }
            }
        )

        wrapper = A2AWrapper(openai_agent=mock_agent)
        wrapper.a2a_skills = [custom_skill]

        # Test skill execution
        result = await custom_skill.handler(wrapper, {"name": "Alice"})
        assert result == {"greeting": "Hello, Alice!"}

        # Test with default parameter
        result = await custom_skill.handler(wrapper, {})
        assert result == {"greeting": "Hello, World!"}

    @pytest.mark.asyncio
    async def test_task_management_workflow(self):
        """Test complete task management workflow."""
        mock_agent = Mock()
        mock_agent.name = "TaskAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Initially no tasks
        assert len(wrapper._tasks) == 0

        # Create and add a task manually (simulating internal processing)
        from a2a_openai_agents.a2a_openai_agents import Task, TaskStatus, Message, Part

        task_id = "test-task-123"
        test_task = Task(
            id=task_id,
            context_id="test-context",
            status=TaskStatus(state="working", message=None)
        )
        wrapper._tasks[task_id] = test_task

        # Test task retrieval
        retrieved_task = await wrapper.get_task(task_id)
        assert retrieved_task == test_task
        assert retrieved_task.status.state == "working"

        # Test task update
        await wrapper.handle_a2a_task_update(
            task_id,
            "completed",
            "Task finished successfully",
            {"output": "processed result"}
        )

        # Verify task was updated
        updated_task = await wrapper.get_task(task_id)
        assert updated_task.status.state == "completed"
        assert updated_task.status.message is None  # A2A uses Message objects, not strings

    def test_multiple_skills_configuration(self):
        """Test configuration with multiple skills."""
        mock_agent = Mock()
        mock_agent.name = "MultiSkillAgent"
        mock_agent.tools = []

        # Create multiple custom skills
        async def skill1_handler(wrapper, params):
            return {"skill": "skill1", "input": params}

        async def skill2_handler(wrapper, params):
            return {"skill": "skill2", "processed": True}

        skills = [
            A2ASkillConfig(
                name="skill_one",
                description="First skill",
                handler=skill1_handler
            ),
            A2ASkillConfig(
                name="skill_two", 
                description="Second skill",
                handler=skill2_handler
            )
        ]

        wrapper = A2AWrapper(openai_agent=mock_agent)
        wrapper.a2a_skills = skills

        # Verify both skills are configured
        assert len(wrapper.a2a_skills) == 2
        assert wrapper.a2a_skills[0].name == "skill_one"
        assert wrapper.a2a_skills[1].name == "skill_two"

        # Verify agent card includes both skills
        agent_card = wrapper._agent_card
        assert len(agent_card.skills) == 2

    def test_agent_with_tools_and_custom_skills_mixed(self):
        """Test agent that has both tools and custom skills."""
        # Mock tool
        mock_tool = Mock()
        mock_tool.name = "builtin_tool"
        mock_tool.description = "Built-in tool"
        mock_tool.params_json_schema = {"type": "object"}

        mock_agent = Mock()
        mock_agent.name = "MixedAgent"
        mock_agent.tools = [mock_tool]

        # Create wrapper (will auto-derive tool skills)
        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Verify auto-derived skill
        assert len(wrapper.a2a_skills) == 1
        assert wrapper.a2a_skills[0].name == "builtin_tool"

        # Add custom skill
        async def custom_handler(wrapper, params):
            return {"custom": True}

        custom_skill = A2ASkillConfig(
            name="custom_skill",
            description="Custom skill",
            handler=custom_handler
        )

        # Override with mixed skills
        wrapper.a2a_skills = wrapper.a2a_skills + [custom_skill]

        # Verify both skills are present
        assert len(wrapper.a2a_skills) == 2
        skill_names = [skill.name for skill in wrapper.a2a_skills]
        assert "builtin_tool" in skill_names
        assert "custom_skill" in skill_names

    def test_wrapper_app_consistency(self):
        """Test that wrapper maintains consistency between skills and app."""
        mock_agent = Mock()
        mock_agent.name = "ConsistentAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Get initial app
        app1 = wrapper.get_app()

        # Add custom skill
        async def test_handler(wrapper, params):
            return {"test": True}

        wrapper.a2a_skills = [A2ASkillConfig(
            name="test_skill",
            description="Test skill",
            handler=test_handler
        )]

        # Get app after skill change - should be reset
        app2 = wrapper.get_app()

        # Apps should be different instances (app gets reset when skills change)
        # This tests the _app = None reset in the skills setter
        assert app1 is not app2