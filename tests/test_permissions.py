from app.core.auth import can_approve_draft, can_draft, can_view_audit


def test_role_permissions() -> None:
    assert can_draft("APP_ANALYST")
    assert not can_approve_draft("APP_ANALYST")
    assert can_approve_draft("APP_MANAGER")
    assert can_view_audit("APP_ADMIN")
    assert can_view_audit("APP_AUDITOR")
