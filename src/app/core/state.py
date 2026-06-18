"""Agent state and context schemas."""

from typing import Annotated, Any
from typing_extensions import TypedDict, NotRequired

from langchain.agents.middleware.types import AgentState, add_messages
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class CustomState(AgentState):
    """Custom agent state extending AgentState with additional fields."""
    question: NotRequired[str]
    answer: NotRequired[str]

class ContextState(BaseModel):
    """Runtime context for agent execution."""
    user_id: str = Field(default="")
    thread_id: str = Field(default="")
