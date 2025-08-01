#!/usr/bin/env python3
"""
A2A OpenAI Agents CLI

Command-line interface for running example agents and demonstrations.
"""

import argparse
import sys


def run_weather_agent(port: int = 8000):
    """Run the simple weather agent example."""
    try:
        import random

        from agents import Agent, function_tool

        from a2a_openai_agents import A2AWrapper, run_a2a_wrapper_server
    except ImportError as e:
        print(f"Error: Required dependencies not installed: {e}")
        print("Install with: pip install a2a-openai-agents")
        sys.exit(1)

    @function_tool
    def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        choices = ["sunny", "cloudy", "rainy", "snowy"]
        return f"The weather in {city} is {random.choice(choices)}."

    # Create the OpenAI Agent
    weather_agent = Agent(
        name="WeatherAssistant",
        instructions="You're a friendly weather assistant. Provide weather information using your tools.",
        model="gpt-4o-mini",
        tools=[get_weather],
    )

    # Wrap with A2A capabilities
    weather_service = A2AWrapper(
        openai_agent=weather_agent,
        a2a_description="An A2A agent that provides weather information for any city.",
    )

    print(f"🌤️  Starting Weather Agent on http://localhost:{port}")
    print(f"   Agent Card: http://localhost:{port}/.well-known/agent.json")
    print("   Press Ctrl+C to stop")

    run_a2a_wrapper_server(weather_service, port=port)


def run_math_agent(port: int = 8001):
    """Run the custom skills math agent example."""
    try:
        from typing import Any

        from agents import Agent

        from a2a_openai_agents import A2ASkillConfig, A2AWrapper, run_a2a_wrapper_server
    except ImportError as e:
        print(f"Error: Required dependencies not installed: {e}")
        print("Install with: pip install a2a-openai-agents")
        sys.exit(1)

    # Create agent
    math_agent = Agent(
        name="MathAssistant",
        instructions="You are a helpful math assistant that can perform calculations.",
        model="gpt-4o-mini",
    )

    # Create wrapper
    math_service = A2AWrapper(
        openai_agent=math_agent,
        a2a_description="An A2A agent that provides mathematical calculation services.",
    )

    # Define custom skills
    async def calculate_sum(wrapper_instance: A2AWrapper, params: dict[str, Any]) -> dict[str, Any]:
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
        wrapper_instance: A2AWrapper, params: dict[str, Any]
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

    # Set custom skills
    math_service.a2a_skills = [
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
    ]

    print(f"🧮 Starting Math Agent on http://localhost:{port}")
    print(f"   Agent Card: http://localhost:{port}/.well-known/agent.json")
    print("   Skills: calculate_sum, calculate_product")
    print("   Press Ctrl+C to stop")

    run_a2a_wrapper_server(math_service, port=port)


def run_multi_agent_demo():
    """Run the multi-agent system demonstration."""
    try:
        import os
        import subprocess
        import sys

        # Get the examples directory
        examples_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "..", "..", "examples"
        )
        script_path = os.path.join(examples_dir, "working_multi_agent.py")

        if not os.path.exists(script_path):
            print("Error: Multi-agent example not found")
            sys.exit(1)

        print("🤖 Starting Multi-Agent System Demo...")
        print("   This will start Calculator and Reporter agents")
        print("   Press Ctrl+C to stop")

        # Run the multi-agent script
        subprocess.run([sys.executable, script_path], check=True)

    except ImportError as e:
        print(f"Error: Required dependencies not installed: {e}")
        print("Install with: pip install a2a-openai-agents")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Multi-agent demo stopped")
    except KeyboardInterrupt:
        print("\nMulti-agent demo stopped")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="A2A OpenAI Agents - Run example agents and demonstrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  a2a-agents weather                    # Start weather agent on port 8000
  a2a-agents math --port 8002          # Start math agent on port 8002  
  a2a-agents multi-agent               # Start multi-agent demonstration
  a2a-agents --version                 # Show version information
        """,
    )

    parser.add_argument("--version", action="version", version="a2a-openai-agents 0.0.1")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Weather agent command
    weather_parser = subparsers.add_parser("weather", help="Run weather agent example")
    weather_parser.add_argument(
        "--port", type=int, default=8000, help="Port to run on (default: 8000)"
    )

    # Math agent command
    math_parser = subparsers.add_parser("math", help="Run math agent with custom skills")
    math_parser.add_argument(
        "--port", type=int, default=8001, help="Port to run on (default: 8001)"
    )

    # Multi-agent command
    subparsers.add_parser("multi-agent", help="Run multi-agent system demonstration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "weather":
            run_weather_agent(args.port)
        elif args.command == "math":
            run_math_agent(args.port)
        elif args.command == "multi-agent":
            run_multi_agent_demo()
    except ImportError as e:
        print(f"Error: Required dependencies not installed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{args.command} agent stopped")


if __name__ == "__main__":
    main()
