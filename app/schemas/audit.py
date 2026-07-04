from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: str
    trace_id: str
    user_id: str
    role: str
    event_type: str
    tool_name: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
