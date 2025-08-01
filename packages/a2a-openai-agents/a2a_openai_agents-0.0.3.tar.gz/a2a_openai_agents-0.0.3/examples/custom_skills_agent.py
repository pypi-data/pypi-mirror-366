#!/usr/bin/env python3
"""
Custom Skills Agent Example

This example demonstrates how to create custom A2A skills that aren't derived from tools.
"""

from typing import Any

# Core dependencies
try:
    from agents import Agent

    from a2a_openai_agents import A2ASkillConfig, A2AWrapper, run_a2a_wrapper_server
except ImportError:
    print("Dependencies not installed. Please run: pip install a2a-openai-agents")
    exit(1)


def main():
    # Create a simple agent brain
    math_agent_brain = Agent(
        name="MathAssistant",
        instructions="You are a helpful math assistant that can perform calculations.",
        model="gpt-4o-mini",
    )

    # Create the A2A wrapper
    math_a2a_service = A2AWrapper(
        openai_agent=math_agent_brain,
        a2a_description="An A2A agent that provides mathematical calculation services.",
    )

    # Define custom A2A skills that aren't derived from tools
    async def calculate_sum(
        _wrapper_instance: A2AWrapper, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate the sum of a list of numbers."""
        numbers = params.get("numbers", [])
        if not isinstance(numbers, list):
            return {"error": "Numbers must be provided as a list"}

        try:
            result = sum(numbers)
            return {"result": result, "operation": "sum", "input": numbers}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid input: {str(e)}"}

    async def calculate_product(
        _wrapper_instance: A2AWrapper, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate the product of a list of numbers."""
        numbers = params.get("numbers", [])
        if not isinstance(numbers, list):
            return {"error": "Numbers must be provided as a list"}

        try:
            result = 1
            for num in numbers:
                result *= num
            return {"result": result, "operation": "product", "input": numbers}
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid input: {str(e)}"}

    async def ai_explain_math(
        wrapper_instance: A2AWrapper, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Use the AI agent to explain a mathematical concept."""
        concept = params.get("concept", "")
        if not concept:
            return {"error": "Concept must be provided"}

        prompt = (
            f"Explain the mathematical concept: {concept}. Provide a clear, concise explanation."
        )
        explanation = await wrapper_instance.process_prompt_with_internal_agent(prompt)
        return {"concept": concept, "explanation": explanation}

    # Override the auto-derived skills with our custom ones
    math_a2a_service.a2a_skills = [
        A2ASkillConfig(
            name="calculate_sum",
            description="Calculate the sum of a list of numbers",
            handler=calculate_sum,
            parameters={
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to sum",
                    }
                },
                "required": ["numbers"],
            },
        ),
        A2ASkillConfig(
            name="calculate_product",
            description="Calculate the product of a list of numbers",
            handler=calculate_product,
            parameters={
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to multiply",
                    }
                },
                "required": ["numbers"],
            },
        ),
        A2ASkillConfig(
            name="explain_math_concept",
            description="Get an AI explanation of a mathematical concept",
            handler=ai_explain_math,
            parameters={
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                        "description": "The mathematical concept to explain",
                    }
                },
                "required": ["concept"],
            },
        ),
    ]

    print("Starting A2A Math Service...")
    print("The service will be available at http://localhost:8001")
    print("Agent Card endpoint: http://localhost:8001/agent-card")
    print("Press Ctrl+C to stop")

    # Start the A2A server
    run_a2a_wrapper_server(math_a2a_service, port=8001)


if __name__ == "__main__":
    main()
