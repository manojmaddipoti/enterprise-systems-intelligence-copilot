from app.api.routes_drafts import approve_draft, reject_draft
from db.duckdb.repository import Repository


def test_approve_draft_writes_audit_event() -> None:
    repo = Repository()
    draft = repo.create_draft(
        draft_type="approval_escalation_note",
        title="Test approval audit",
        body="Synthetic approval audit test.",
        created_by="test_analyst",
    )

    approved = approve_draft(draft["draft_id"], user_id="test_manager", role="APP_MANAGER")

    assert approved["status"] == "APPROVED"
    events = repo.list_audit_events()
    assert any(
        event["event_type"] == "draft_approved" and draft["draft_id"] in event["details"]
        for event in events
    )


def test_reject_draft_writes_audit_event() -> None:
    repo = Repository()
    draft = repo.create_draft(
        draft_type="approval_escalation_note",
        title="Test rejection audit",
        body="Synthetic rejection audit test.",
        created_by="test_analyst",
    )

    rejected = reject_draft(draft["draft_id"], user_id="test_manager", role="APP_MANAGER")

    assert rejected["status"] == "REJECTED"
    events = repo.list_audit_events()
    assert any(
        event["event_type"] == "draft_rejected" and draft["draft_id"] in event["details"]
        for event in events
    )
