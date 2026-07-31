from typing import Any, Literal

from pydantic import BaseModel, Field

RoleLiteral = Literal["APP_ANALYST", "APP_MANAGER", "APP_ADMIN", "APP_AUDITOR"]


class ChatRequest(BaseModel):
    user_id: str = "demo_analyst"
    role: RoleLiteral = "APP_ANALYST"
    message: str
    session_id: str | None = None


class Citation(BaseModel):
    source: str
    reference: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
    intent: str
    tools_called: list[str]
    citations: list[Citation] = Field(default_factory=list)
    requires_approval: bool = False
    draft_id: str | None = None
    trace_id: str
