"""A2A OpenAI Agents - Integration library for OpenAI Agents with A2A Protocol."""

from .a2a_openai_agents import A2ASkillConfig, A2AWrapper, run_a2a_wrapper_server

__version__ = "0.0.1"

__all__ = (
    "A2AWrapper",
    "A2ASkillConfig",
    "run_a2a_wrapper_server",
)
