from enum import StrEnum


class Role(StrEnum):
    analyst = "APP_ANALYST"
    manager = "APP_MANAGER"
    admin = "APP_ADMIN"
    auditor = "APP_AUDITOR"


def can_draft(role: str) -> bool:
    return role in {Role.analyst, Role.manager, Role.admin}


def can_approve_draft(role: str) -> bool:
    return role in {Role.manager, Role.admin}


def can_view_audit(role: str) -> bool:
    return role in {Role.admin, Role.auditor}


def can_view_sensitive(role: str) -> bool:
    return role == Role.admin


def can_view_partial_sensitive(role: str) -> bool:
    return role in {Role.manager, Role.admin}
