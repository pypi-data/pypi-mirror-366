"""Tests for A2AWrapper functionality."""

import pytest
from unittest.mock import Mock, AsyncMock

from a2a_openai_agents import A2AWrapper, A2ASkillConfig


class TestA2AWrapper:
    """Test A2AWrapper class functionality."""

    def test_wrapper_initialization(self):
        """Test basic A2AWrapper initialization."""
        # Mock Agent
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(
            openai_agent=mock_agent,
            a2a_description="Test wrapper"
        )

        assert wrapper._openai_agent == mock_agent
        assert wrapper._a2a_name == "TestAgent"
        assert wrapper._a2a_description == "Test wrapper"
        assert wrapper._a2a_version == "1.0.0"
        assert wrapper._a2a_id == "testagent"  # slugified
        assert isinstance(wrapper._tasks, dict)

    def test_wrapper_with_custom_values(self):
        """Test A2AWrapper with custom configuration."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(
            openai_agent=mock_agent,
            a2a_name="CustomName",
            a2a_description="Custom description",
            a2a_version="2.0.0",
            a2a_id="custom-id"
        )

        assert wrapper._a2a_name == "CustomName"
        assert wrapper._a2a_description == "Custom description"
        assert wrapper._a2a_version == "2.0.0"
        assert wrapper._a2a_id == "custom-id"

    def test_slugify_method(self):
        """Test the _slugify static method."""
        assert A2AWrapper._slugify("Test Agent") == "test-agent"
        assert A2AWrapper._slugify("Test_Agent!") == "test_agent"
        assert A2AWrapper._slugify("Test  Multiple  Spaces") == "test-multiple-spaces"
        assert A2AWrapper._slugify("Test-Agent") == "test-agent"

    def test_skill_derivation_no_tools(self):
        """Test skill derivation when agent has no tools."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)
        skills = wrapper._derive_skills_from_tools()

        assert skills == []

    def test_skill_derivation_with_tools(self):
        """Test skill derivation when agent has tools."""
        # Mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool description"
        mock_tool.params_json_schema = {"type": "object", "properties": {"param": {"type": "string"}}}

        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = [mock_tool]

        wrapper = A2AWrapper(openai_agent=mock_agent)
        skills = wrapper._derive_skills_from_tools()

        assert len(skills) == 1
        assert skills[0].name == "test_tool"
        assert skills[0].description == "Test tool description"
        assert skills[0].parameters == {"type": "object", "properties": {"param": {"type": "string"}}}

    def test_custom_skills_override(self):
        """Test that custom skills can override auto-derived ones."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        async def custom_handler(wrapper, params):
            return {"result": "custom"}

        custom_skill = A2ASkillConfig(
            name="custom_skill",
            description="Custom skill",
            handler=custom_handler
        )

        wrapper = A2AWrapper(openai_agent=mock_agent)
        wrapper.a2a_skills = [custom_skill]

        assert len(wrapper.a2a_skills) == 1
        assert wrapper.a2a_skills[0].name == "custom_skill"

    def test_agent_card_creation(self):
        """Test agent card creation."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(
            openai_agent=mock_agent,
            a2a_description="Test agent"
        )

        agent_card = wrapper._agent_card

        assert agent_card.name == "TestAgent"
        assert agent_card.description == "Test agent"
        assert agent_card.version == "1.0.0"
        assert agent_card.url == "http://localhost:8000"
        assert agent_card.default_input_modes == ["text"]
        assert agent_card.default_output_modes == ["text"]

    def test_get_app_creates_fastapi_app(self):
        """Test that get_app creates and returns a FastAPI application."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)
        app = wrapper.get_app()

        # Should create an A2AFastAPIApplication
        assert app is not None
        assert hasattr(app, 'build')  # Should have build method

    def test_skills_property_getter_setter(self):
        """Test the a2a_skills property getter and setter."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Test getter
        initial_skills = wrapper.a2a_skills
        assert initial_skills == []

        # Test setter
        async def test_handler(wrapper, params):
            return {"test": True}

        new_skill = A2ASkillConfig(
            name="test_skill",
            description="Test skill",
            handler=test_handler
        )

        wrapper.a2a_skills = [new_skill]
        assert len(wrapper.a2a_skills) == 1
        assert wrapper.a2a_skills[0].name == "test_skill"

    @pytest.mark.asyncio
    async def test_get_task(self):
        """Test get_task method."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Test getting non-existent task
        result = await wrapper.get_task("non-existent")
        assert result is None

        # Add a mock task
        from a2a_openai_agents.a2a_openai_agents import Task, TaskStatus
        mock_task = Task(
            id="test-task",
            context_id="test-context",
            status=TaskStatus(state="completed", message=None)
        )
        wrapper._tasks["test-task"] = mock_task

        # Test getting existing task
        result = await wrapper.get_task("test-task")
        assert result == mock_task

    @pytest.mark.asyncio
    async def test_handle_a2a_task_update(self):
        """Test handle_a2a_task_update method."""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.tools = []

        wrapper = A2AWrapper(openai_agent=mock_agent)

        # Add a mock task
        from a2a_openai_agents.a2a_openai_agents import Task, TaskStatus
        mock_task = Task(
            id="test-task",
            context_id="test-context",
            status=TaskStatus(state="working", message=None)
        )
        wrapper._tasks["test-task"] = mock_task

        # Update the task
        await wrapper.handle_a2a_task_update(
            "test-task",
            "completed",
            "Task finished",
            {"output": "result"}
        )

        # Check the task was updated
        updated_task = wrapper._tasks["test-task"]
        assert updated_task.status.state == "completed"
        assert updated_task.status.message is None  # A2A uses Message objects, not strings


class TestA2ASkillConfig:
    """Test A2ASkillConfig class."""

    def test_skill_config_initialization(self):
        """Test A2ASkillConfig initialization."""
        async def test_handler(wrapper, params):
            return {"result": "test"}

        config = A2ASkillConfig(
            name="test_skill",
            description="Test skill description",
            handler=test_handler,
            parameters={"type": "object"}
        )

        assert config.name == "test_skill"
        assert config.description == "Test skill description" 
        assert config.handler == test_handler
        assert config.parameters == {"type": "object"}

    def test_skill_config_default_parameters(self):
        """Test A2ASkillConfig with default parameters."""
        async def test_handler(wrapper, params):
            return {"result": "test"}

        config = A2ASkillConfig(
            name="test_skill",
            description="Test skill description",
            handler=test_handler
        )

        assert config.parameters == {}