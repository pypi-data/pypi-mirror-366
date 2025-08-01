#!/usr/bin/env python3
"""
Simple Weather Agent Example

This example demonstrates how to create a basic A2A-enabled agent that provides weather information.
"""

import random

# Core dependencies (these would be installed via pip install a2a-openai-agents)
try:
    from agents import Agent, function_tool

    from a2a_openai_agents import A2AWrapper, run_a2a_wrapper_server
except ImportError:
    print("Dependencies not installed. Please run: pip install a2a-openai-agents")
    exit(1)


# Define a simple weather tool
@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


def main():
    # Create the core OpenAI Agent (the "brain")
    weather_agent_brain = Agent(
        name="WeatherAssistant",
        instructions="You're a friendly weather assistant. Provide weather information using your tools.",
        model="gpt-4o-mini",
        tools=[get_weather],
    )

    # Wrap the agent with A2A capabilities
    weather_a2a_service = A2AWrapper(
        openai_agent=weather_agent_brain,
        a2a_description="An A2A agent that provides weather information for any city.",
    )

    print("Starting A2A Weather Service...")
    print("The service will be available at http://localhost:8000")
    print("Agent Card endpoint: http://localhost:8000/agent-card")
    print("Press Ctrl+C to stop")

    # Start the A2A server
    run_a2a_wrapper_server(weather_a2a_service, port=8000)


if __name__ == "__main__":
    main()
