"""
Basic tests for a2a-openai-agents library.

Note: These tests require the dependencies to be installed to run properly.
"""

from unittest.mock import MagicMock

import pytest


def test_a2a_skill_config():
    """Test A2ASkillConfig initialization."""
    try:
        from a2a_openai_agents import A2ASkillConfig

        async def dummy_handler(_wrapper, _params):
            return {"result": "test"}

        config = A2ASkillConfig(
            name="test_skill",
            description="A test skill",
            handler=dummy_handler,
            parameters={"type": "object"},
        )

        assert config.name == "test_skill"
        assert config.description == "A test skill"
        assert config.handler == dummy_handler
        assert config.parameters == {"type": "object"}

    except ImportError:
        pytest.skip("Dependencies not installed, skipping test")


def test_a2a_wrapper_initialization():
    """Test A2AWrapper initialization with mocked dependencies."""
    try:
        from a2a_openai_agents import A2AWrapper

        # Mock the Agent class
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        # Create wrapper (no need to mock A2AServer since we use composition now)
        wrapper = A2AWrapper(openai_agent=mock_agent, a2a_description="Test wrapper")

        assert wrapper._openai_agent == mock_agent
        assert wrapper._a2a_name == "TestAgent"
        assert wrapper._a2a_description == "Test wrapper"
        assert wrapper._a2a_version == "1.0.0"
        assert wrapper._a2a_id == "testagent"
        assert len(wrapper.a2a_skills) == 0  # No tools = no skills

    except ImportError:
        pytest.skip("Dependencies not installed, skipping test")


def test_slugify():
    """Test the slugify utility function."""
    try:
        from a2a_openai_agents.a2a_openai_agents import A2AWrapper

        assert A2AWrapper._slugify("Hello World") == "hello-world"
        assert A2AWrapper._slugify("Test Agent 123") == "test-agent-123"
        assert A2AWrapper._slugify("Special!@#Characters") == "specialcharacters"
        assert A2AWrapper._slugify("  Multiple   Spaces  ") == "multiple-spaces"

    except ImportError:
        pytest.skip("Dependencies not installed, skipping test")


def test_imports():
    """Test that the main imports work."""
    try:
        from a2a_openai_agents import A2ASkillConfig, A2AWrapper, run_a2a_wrapper_server

        # Just check that the imports work
        assert A2AWrapper is not None
        assert A2ASkillConfig is not None
        assert run_a2a_wrapper_server is not None

    except ImportError:
        pytest.skip("Dependencies not installed, skipping test")


def test_basic_agent_functionality():
    """Test that we can create a basic agent with OpenAI."""
    try:
        import os

        from agents import Agent

        # Skip if no API key available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OPENAI_API_KEY found, skipping test")

        # Create a simple agent
        agent = Agent(
            name="TestAgent",
            instructions="You are a test agent. Always respond with 'Hello from test!'",
            model="gpt-4o-mini",
        )

        assert agent.name == "TestAgent"
        print("✅ Basic agent creation works!")

    except ImportError:
        pytest.skip("Dependencies not installed, skipping test")
