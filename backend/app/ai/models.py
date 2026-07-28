from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    name: str | None = None


class MemoryItem(BaseModel):
    id: UUID | None = None
    score: float = 0.0
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    full_name: str
    language: str
    timezone: str
    preferences: dict[str, Any] = Field(default_factory=dict)


class AIContext(BaseModel):
    system_prompt: str
    profile: UserProfile
    memories: list[MemoryItem] = Field(default_factory=list)
    conversation: list[ChatMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIRequest(BaseModel):
    user_id: UUID
    message: str
    conversation_id: UUID | None = None
    stream: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIResponse(BaseModel):
    message: str
    provider: AIProvider
    model: str
    usage: AIUsage
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)