from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.auth import can_view_sensitive
from db.duckdb.repository import Repository

POLICY_DIR = Path("data/policies")
SENSITIVE_KEYS = {"tax_id", "bank_account_number", "personal_email", "personal_phone"}


def mask_value(key: str, value: Any, role: str) -> Any:
    if value in (None, "") or can_view_sensitive(role):
        return value
    text = str(value)
    if key == "tax_id":
        return f"***-**-{text[-4:]}"
    if key == "bank_account_number":
        return f"********{text[-4:]}"
    if key == "personal_email":
        local, _, domain = text.partition("@")
        return f"{local[:1]}***@{domain}" if domain else "***"
    if key == "personal_phone":
        digits = "".join(ch for ch in text if ch.isdigit())
        return f"(***) ***-{digits[-4:]}" if len(digits) >= 4 else "(***) ***-****"
    return "***"


def mask_record(record: dict[str, Any], role: str) -> dict[str, Any]:
    return {key: mask_value(key, value, role) if key in SENSITIVE_KEYS else value for key, value in record.items()}


def mask_records(records: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    return [mask_record(record, role) for record in records]


class EnterpriseTools:
    def __init__(self, repo: Repository | None = None) -> None:
        self.repo = repo or Repository()

    def query_invoice_exceptions(self, role: str) -> list[dict[str, Any]]:
        return mask_records(self.repo.top_blocked_suppliers(), role)

    def query_approval_bottlenecks(self, role: str) -> list[dict[str, Any]]:
        return mask_records(self.repo.slowest_approval_bottlenecks(), role)

    def query_no_receipt_percentage(self) -> dict[str, Any]:
        return self.repo.no_receipt_percentage()

    def query_coupa_not_oracle(self, role: str) -> list[dict[str, Any]]:
        return mask_records(self.repo.coupa_not_oracle_suppliers(), role)

    def query_missing_oracle_invoice(self, role: str) -> list[dict[str, Any]]:
        return mask_records(self.repo.coupa_po_missing_oracle_invoice(), role)

    def query_invoice_reason(self, invoice_number: str, role: str) -> dict[str, Any] | None:
        invoice = self.repo.invoice_by_number(invoice_number)
        return mask_record(invoice, role) if invoice else None

    def search_policy_documents(self, query: str) -> list[dict[str, Any]]:
        terms = {term.lower() for term in query.replace("$", " ").replace(",", " ").split() if len(term) > 2}
        matches: list[dict[str, Any]] = []
        for path in sorted(POLICY_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            haystack = text.lower()
            score = sum(1 for term in terms if term in haystack)
            if score or "policy" in query.lower():
                excerpt = " ".join(text.split())[:500]
                matches.append({"source": path.name, "score": score, "excerpt": excerpt})
        return sorted(matches, key=lambda item: item["score"], reverse=True)[:3]

    def create_draft_action(self, user_id: str, title: str, body: str) -> dict[str, Any]:
        return self.repo.create_draft(
            draft_type="approval_escalation_note",
            title=title,
            body=body,
            created_by=user_id,
        )
