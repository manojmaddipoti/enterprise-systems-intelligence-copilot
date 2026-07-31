from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DraftStatus = Literal["PENDING_APPROVAL", "APPROVED", "REJECTED"]


class DraftAction(BaseModel):
    draft_id: str
    draft_type: str
    title: str
    body: str
    status: DraftStatus
    created_by: str
    approved_by: str | None = None
    created_at: datetime
    updated_at: datetime
