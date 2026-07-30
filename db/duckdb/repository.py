from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from app.core.config import get_settings


class Repository:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or get_settings().duckdb_path

    def _connect(self) -> duckdb.DuckDBPyConnection:
        if not Path(self.db_path).exists():
            raise RuntimeError("DuckDB database not found. Run `make seed` and `make init-db` first.")
        return duckdb.connect(self.db_path)

    def health(self) -> dict[str, Any]:
        with self._connect() as con:
            supplier_count = con.execute("SELECT COUNT(*) FROM RAW_ORACLE_SUPPLIERS").fetchone()[0]
            invoice_count = con.execute("SELECT COUNT(*) FROM RAW_ORACLE_AP_INVOICES").fetchone()[0]
        return {"status": "ok", "supplier_count": supplier_count, "invoice_count": invoice_count}

    def workflow_health(self, limit: int = 24) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT * FROM MART_ENTERPRISE_WORKFLOW_HEALTH
            ORDER BY period DESC, workflow_health_score ASC
            LIMIT ?
            """,
            [limit],
        )

    def invoice_exceptions(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT * FROM MART_INVOICE_EXCEPTIONS
            ORDER BY open_amount DESC, days_pending DESC
            LIMIT ?
            """,
            [limit],
        )

    def supplier_360(self, supplier_id: str) -> dict[str, Any] | None:
        rows = self._rows(
            """
            SELECT * FROM MART_SUPPLIER_360
            WHERE enterprise_supplier_id = ? OR oracle_supplier_id = ? OR coupa_supplier_id = ?
            LIMIT 1
            """,
            [supplier_id, supplier_id, supplier_id],
        )
        return rows[0] if rows else None

    def top_blocked_suppliers(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT supplier_name, business_unit, SUM(open_amount) AS blocked_invoice_amount, COUNT(*) AS blocked_invoice_count
            FROM MART_INVOICE_EXCEPTIONS
            GROUP BY supplier_name, business_unit
            ORDER BY blocked_invoice_amount DESC
            LIMIT ?
            """,
            [limit],
        )

    def slowest_approval_bottlenecks(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT business_unit, approver_role, approver_name, avg_cycle_time_hours, pending_count, overdue_count, total_amount_pending
            FROM MART_APPROVAL_BOTTLENECKS
            ORDER BY avg_cycle_time_hours DESC, total_amount_pending DESC
            LIMIT ?
            """,
            [limit],
        )

    def no_receipt_percentage(self) -> dict[str, Any]:
        rows = self._rows(
            """
            SELECT
              COUNT(*) AS total_invoices,
              SUM(CASE WHEN has_receipt_match THEN 0 ELSE 1 END) AS no_receipt_invoices,
              ROUND(SUM(CASE WHEN has_receipt_match THEN 0 ELSE 1 END) * 100.0 / COUNT(*), 2) AS percentage
            FROM MART_PO_INVOICE_MATCHING
            """,
            [],
        )
        return rows[0]

    def user_role_count(self) -> int:
        rows = self._rows("SELECT COUNT(*) AS role_count FROM APP_USER_ROLES", [])
        return rows[0]["role_count"]

    def coupa_not_oracle_suppliers(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT c.coupa_supplier_id, c.supplier_name, c.region, c.commodity, c.payment_terms
            FROM RAW_COUPA_SUPPLIERS c
            LEFT JOIN RAW_ORACLE_SUPPLIERS o ON c.enterprise_supplier_id = o.enterprise_supplier_id
            WHERE o.oracle_supplier_id IS NULL
            ORDER BY c.supplier_name
            LIMIT ?
            """,
            [limit],
        )

    def coupa_po_missing_oracle_invoice(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._rows(
            """
            SELECT
              p.po_number,
              p.coupa_supplier_id,
              p.business_unit,
              p.po_amount,
              CAST(p.approved_at AS VARCHAR) AS approved_at
            FROM RAW_COUPA_PURCHASE_ORDERS p
            LEFT JOIN RAW_ORACLE_AP_INVOICES i ON p.po_number = i.po_number
            WHERE p.status = 'APPROVED' AND i.invoice_id IS NULL
            ORDER BY p.po_amount DESC
            LIMIT ?
            """,
            [limit],
        )

    def invoice_by_number(self, invoice_number: str) -> dict[str, Any] | None:
        normalized = invoice_number if invoice_number.startswith("INV-") else f"INV-{invoice_number}"
        rows = self._rows(
            """
            SELECT *
            FROM MART_INVOICE_EXCEPTIONS
            WHERE invoice_number = ? OR invoice_id = ?
            LIMIT 1
            """,
            [normalized, normalized],
        )
        return rows[0] if rows else None

    def create_draft(self, draft_type: str, title: str, body: str, created_by: str) -> dict[str, Any]:
        now = datetime.now(UTC)
        draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO APP_DRAFT_ACTIONS
                VALUES (?, ?, ?, ?, 'PENDING_APPROVAL', ?, NULL, ?, ?)
                """,
                [draft_id, draft_type, title, body, created_by, now, now],
            )
        return self.get_draft(draft_id) or {}

    def get_draft(self, draft_id: str) -> dict[str, Any] | None:
        rows = self._rows("SELECT * FROM APP_DRAFT_ACTIONS WHERE draft_id = ?", [draft_id])
        return rows[0] if rows else None

    def list_drafts(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM APP_DRAFT_ACTIONS ORDER BY created_at DESC", [])

    def update_draft_status(self, draft_id: str, status: str, approved_by: str) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        with self._connect() as con:
            con.execute(
                """
                UPDATE APP_DRAFT_ACTIONS
                SET status = ?, approved_by = ?, updated_at = ?
                WHERE draft_id = ?
                """,
                [status, approved_by, now, draft_id],
            )
        return self.get_draft(draft_id)

    def log_audit(
        self,
        trace_id: str,
        user_id: str,
        role: str,
        event_type: str,
        tool_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO APP_AUDIT_EVENTS
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    f"AUD-{uuid.uuid4().hex[:10].upper()}",
                    trace_id,
                    user_id,
                    role,
                    event_type,
                    tool_name,
                    json.dumps(details or {}),
                    datetime.now(UTC),
                ],
            )

    def list_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._rows(
            "SELECT * FROM APP_AUDIT_EVENTS ORDER BY created_at DESC LIMIT ?",
            [limit],
        )

    def record_feedback(self, trace_id: str, user_id: str, rating: int, comment: str) -> dict[str, Any]:
        feedback_id = f"FDB-{uuid.uuid4().hex[:8].upper()}"
        with self._connect() as con:
            con.execute(
                "INSERT INTO APP_AGENT_FEEDBACK VALUES (?, ?, ?, ?, ?, ?)",
                [feedback_id, trace_id, user_id, rating, comment, datetime.now(UTC)],
            )
        return {"feedback_id": feedback_id, "status": "recorded"}

    def store_eval_result(
        self,
        run_id: str,
        eval_id: str,
        passed: bool,
        intent: str,
        tools_called: list[str],
        latency_ms: int,
    ) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO APP_EVAL_RESULTS VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    run_id,
                    eval_id,
                    passed,
                    intent,
                    ",".join(tools_called),
                    latency_ms,
                    datetime.now(UTC),
                ],
            )

    def eval_results(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM APP_EVAL_RESULTS ORDER BY created_at DESC LIMIT ?", [limit])

    def _rows(self, query: str, params: list[Any]) -> list[dict[str, Any]]:
        with self._connect() as con:
            result = con.execute(query, params)
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row, strict=False)) for row in result.fetchall()]
