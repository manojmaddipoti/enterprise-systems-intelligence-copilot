from fastapi import APIRouter

from app.core.auth import can_view_audit
from app.core.exceptions import forbidden
from db.duckdb.repository import Repository

router = APIRouter()


@router.get("/audit/events")
def audit_events(role: str = "APP_ADMIN") -> list[dict]:
    if not can_view_audit(role):
        raise forbidden("Only APP_ADMIN and APP_AUDITOR can view audit events.")
    return Repository().list_audit_events()
