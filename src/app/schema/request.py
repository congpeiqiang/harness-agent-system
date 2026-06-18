"""Request schema models for the LangGraph API."""

from typing import Any
from pydantic import BaseModel, Field


class InvokeRequest(BaseModel):
    """Request body for /invoke."""

    messages: list[dict[str, Any]] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class StreamRequest(BaseModel):
    """Request body for /stream."""

    messages: list[dict[str, Any]] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class BatchRequest(BaseModel):
    """Request body for /batch."""

    inputs: list[dict[str, Any]] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class ThreadStateUpdate(BaseModel):
    """Request body for updating thread state."""

    state: dict[str, Any] = Field(default_factory=dict)
