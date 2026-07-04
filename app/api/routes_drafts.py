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
    if not can_approve_draft(role):
        raise forbidden("Only APP_MANAGER and APP_ADMIN can approve draft actions.")
    draft = Repository().update_draft_status(draft_id, "APPROVED", user_id)
    if not draft:
        raise not_found("Draft not found.")
    return draft


@router.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: str, user_id: str = "demo_manager", role: str = "APP_MANAGER") -> dict:
    if not can_approve_draft(role):
        raise forbidden("Only APP_MANAGER and APP_ADMIN can reject draft actions.")
    draft = Repository().update_draft_status(draft_id, "REJECTED", user_id)
    if not draft:
        raise not_found("Draft not found.")
    return draft
