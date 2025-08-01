# a2a-openai-agents

A robust and elegant Python library for integrating OpenAI Agents (built with the `openai-agents` SDK) with the A2A (Agent2Agent) Protocol.

## Overview

The `a2a-openai-agents` library enables developers to expose their intelligent `agents.Agent` instances as interoperable A2A services with minimal configuration. It prioritizes clear separation of concerns, automatic configuration, and a highly Pythonic developer experience for both synchronous and durable agent operations.

## Key Features

- **Composition-Based Integration**: Wrap existing `agents.Agent` instances without modification
- **Automatic A2A Derivation**: Sensible A2A metadata and skills derived from agent configuration
- **Default Synchronous Simplicity**: Minimal setup for straightforward agent interactions
- **Opt-in Durable Operations**: Support for long-running tasks via Temporal.io
- **Protocol-Native Task Management**: Leverages A2A's native `Task` model consistently

## Installation

```bash
pip install a2a-openai-agents
```

## Quick Start

### Simple Weather Agent

```python
import random
from agents import Agent
from agents.tools import function_tool
from a2a_openai_agents import A2AWrapper, run_a2a_wrapper_server

@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."

# Create your OpenAI Agent
weather_agent = Agent(
    name="WeatherAssistant",
    instructions="You're a friendly weather assistant.",
    model="gpt-4o-mini",
    tools=[get_weather],
)

# Wrap with A2A capabilities
weather_service = A2AWrapper(
    openai_agent=weather_agent,
    a2a_description="An A2A agent that provides weather information.",
)

# Start the A2A server
run_a2a_wrapper_server(weather_service, port=8000)
```

### Custom Skills Example

```python
from agents import Agent
from a2a_openai_agents import A2AWrapper, A2ASkillConfig, run_a2a_wrapper_server

# Create agent
math_agent = Agent(
    name="MathAssistant",
    instructions="You are a helpful math assistant.",
    model="gpt-4o-mini",
)

# Create wrapper
math_service = A2AWrapper(
    openai_agent=math_agent,
    a2a_description="Mathematical calculation services.",
)

# Define custom skill
async def calculate_sum(wrapper_instance, params):
    numbers = params.get("numbers", [])
    return {"result": sum(numbers)}

# Override with custom skills
math_service.a2a_skills = [
    A2ASkillConfig(
        name="calculate_sum",
        description="Calculate the sum of numbers",
        handler=calculate_sum,
        parameters={
            "type": "object",
            "properties": {
                "numbers": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["numbers"]
        }
    )
]

run_a2a_wrapper_server(math_service, port=8001)
```

## API Reference

### A2AWrapper

Main class for wrapping `agents.Agent` instances to expose them as A2A services.

```python
A2AWrapper(
    openai_agent: Agent,                    # Required: Your Agent instance
    a2a_name: Optional[str] = None,         # Defaults to agent.name
    a2a_description: Optional[str] = None,  # Recommended for clarity
    a2a_version: str = "1.0.0",            # Version string
    a2a_id: Optional[str] = None,          # Defaults to slugified name
    a2a_skills: Optional[List[A2ASkillConfig]] = None  # Auto-derived if None
)
```

### A2ASkillConfig

Configuration for defining A2A skills.

```python
A2ASkillConfig(
    name: str,                              # Skill name
    description: str,                       # Human-readable description
    handler: Callable,                      # Async handler function
    parameters: Optional[Dict[str, Any]]    # JSON Schema for parameters
)
```

### run_a2a_wrapper_server

Convenience function to start the A2A HTTP server.

```python
run_a2a_wrapper_server(
    wrapper_instance: A2AWrapper,
    port: int = 8000,
    host: str = "0.0.0.0"
)
```

## Architecture

### Composition Over Inheritance

The library uses composition rather than inheritance. Your `agents.Agent` instances remain pure and unmodified, while `A2AWrapper` adds A2A interoperability around them.

### Automatic Skill Derivation

By default, A2A skills are automatically derived from your agent's `tools`. Each tool becomes an A2A skill with appropriate parameter schemas.

### Task Management

- **Synchronous**: Handlers returning `Dict` are automatically wrapped in `COMPLETED` A2A Tasks
- **Durable**: Handlers returning `a2a_sdk.models.Task` enable long-running operations

## Examples

See the `examples/` directory for complete working examples:

- `simple_weather_agent.py`: Basic agent with tool-derived skills
- `custom_skills_agent.py`: Agent with custom A2A skills

## Development

For development setup and workflows, see [development.md](development.md).

For publishing instructions, see [publishing.md](publishing.md).

## License

MIT License. See [LICENSE](LICENSE) for details.
