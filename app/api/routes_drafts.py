import uuid

from fastapi import APIRouter

from app.core.auth import can_approve_draft
from app.core.exceptions import forbidden, not_found
from db.duckdb.repository import Repository

router = APIRouter()


@router.get("/drafts")
def drafts() -> list[dict]:
    return Repository().list_drafts()


@router.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: str, user_id: str = "demo_manager", role: str = "APP_MANAGER") -> dict:
    repo = Repository()
    trace_id = f"TRACE-{uuid.uuid4().hex[:10].upper()}"
    if not can_approve_draft(role):
        repo.log_audit(
            trace_id=trace_id,
            user_id=user_id,
            role=role,
            event_type="draft_approval_denied",
            tool_name="update_draft_status",
            details={"draft_id": draft_id, "requested_status": "APPROVED"},
        )
        raise forbidden("Only APP_MANAGER and APP_ADMIN can approve draft actions.")
    draft = repo.update_draft_status(draft_id, "APPROVED", user_id)
    if not draft:
        raise not_found("Draft not found.")
    repo.log_audit(
        trace_id=trace_id,
        user_id=user_id,
        role=role,
        event_type="draft_approved",
        tool_name="update_draft_status",
        details={"draft_id": draft_id, "status": "APPROVED"},
    )
    return draft


@router.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: str, user_id: str = "demo_manager", role: str = "APP_MANAGER") -> dict:
    repo = Repository()
    trace_id = f"TRACE-{uuid.uuid4().hex[:10].upper()}"
    if not can_approve_draft(role):
        repo.log_audit(
            trace_id=trace_id,
            user_id=user_id,
            role=role,
            event_type="draft_rejection_denied",
            tool_name="update_draft_status",
            details={"draft_id": draft_id, "requested_status": "REJECTED"},
        )
        raise forbidden("Only APP_MANAGER and APP_ADMIN can reject draft actions.")
    draft = repo.update_draft_status(draft_id, "REJECTED", user_id)
    if not draft:
        raise not_found("Draft not found.")
    repo.log_audit(
        trace_id=trace_id,
        user_id=user_id,
        role=role,
        event_type="draft_rejected",
        tool_name="update_draft_status",
        details={"draft_id": draft_id, "status": "REJECTED"},
    )
    return draft
