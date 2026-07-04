from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from time import perf_counter

from app.core.auth import can_draft
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from db.duckdb.repository import Repository

from .tools import EnterpriseTools


@dataclass
class AgentResult:
    response: ChatResponse
    latency_ms: int


class Orchestrator:
    def __init__(self, repo: Repository | None = None) -> None:
        self.repo = repo or Repository()
        self.tools = EnterpriseTools(self.repo)

    def handle(self, request: ChatRequest) -> ChatResponse:
        started = perf_counter()
        trace_id = f"TRACE-{uuid.uuid4().hex[:10].upper()}"
        message = request.message.strip()
        lower = message.lower()
        tools_called: list[str] = []
        citations: list[Citation] = []
        requires_approval = False
        draft_id: str | None = None

        if self._is_security_denial(lower):
            intent = "security_denial"
            answer = (
                "I cannot run raw SQL, reveal raw source tables, expose unmasked sensitive fields, "
                "or accept role changes from prompt text. Use approved marts, governed tools, and app roles."
            )
            self._audit(trace_id, request, intent, None, {"reason": "security_denial"})
            return ChatResponse(
                answer=answer,
                intent=intent,
                tools_called=tools_called,
                citations=citations,
                requires_approval=False,
                draft_id=None,
                trace_id=trace_id,
            )

        if "draft" in lower or "escalation" in lower:
            intent = "action_drafting"
            tools_called.append("create_draft_action")
            if not can_draft(request.role):
                answer = "Your role can view governed information, but it cannot create internal draft actions."
                self._audit(trace_id, request, intent, "create_draft_action", {"allowed": False})
            else:
                rows = self.tools.query_invoice_exceptions(request.role)
                target = rows[0] if rows else {"supplier_name": "the top blocked supplier", "blocked_invoice_amount": 0}
                draft = self.tools.create_draft_action(
                    request.user_id,
                    "Escalation note for blocked invoice follow-up",
                    (
                        f"Please review blocked invoice exposure for {target['supplier_name']}. "
                        f"Current blocked amount is {target['blocked_invoice_amount']}. "
                        "Recommended next step: confirm receipt, approval, or variance resolution before release."
                    ),
                )
                draft_id = draft["draft_id"]
                requires_approval = True
                answer = (
                    f"I created internal draft {draft_id}. It remains pending and requires manager or admin "
                    "approval before any action is considered complete."
                )
                self._audit(trace_id, request, intent, "create_draft_action", {"draft_id": draft_id})

        elif "three-way" in lower or "policy" in lower or "approval level" in lower or "paid without receipt" in lower:
            intent = "policy_lookup"
            tools_called.append("search_policy_documents")
            matches = self.tools.search_policy_documents(message)
            citations = [
                Citation(source="policy_document", reference=match["source"], metadata={"score": match["score"]})
                for match in matches
            ]
            answer = self._format_policy_answer(message, matches)
            self._audit(trace_id, request, intent, "search_policy_documents", {"matches": len(matches)})

        elif "slowest approval" in lower or "approval cycle" in lower or "bottleneck" in lower:
            intent = "structured_data"
            tools_called.append("query_approval_bottlenecks")
            rows = self.tools.query_approval_bottlenecks(request.role)
            answer = self._format_table_answer("Slowest approval bottlenecks", rows)
            citations.append(Citation(source="mart", reference="MART_APPROVAL_BOTTLENECKS"))
            self._audit(trace_id, request, intent, "query_approval_bottlenecks", {"rows": len(rows)})

        elif "no matching receipt" in lower or "without receipt" in lower:
            intent = "structured_data"
            tools_called.append("query_po_invoice_matching")
            result = self.tools.query_no_receipt_percentage()
            answer = (
                f"{result['percentage']}% of invoices have no matching receipt "
                f"({result['no_receipt_invoices']} of {result['total_invoices']} invoices)."
            )
            citations.append(Citation(source="mart", reference="MART_PO_INVOICE_MATCHING"))
            self._audit(trace_id, request, intent, "query_po_invoice_matching", result)

        elif "coupa but not oracle" in lower:
            intent = "structured_data"
            tools_called.append("query_supplier_xref")
            rows = self.tools.query_coupa_not_oracle(request.role)
            answer = self._format_table_answer("Suppliers in Coupa but not Oracle", rows)
            citations.append(Citation(source="raw_controlled_join", reference="RAW_COUPA_SUPPLIERS to RAW_ORACLE_SUPPLIERS"))
            self._audit(trace_id, request, intent, "query_supplier_xref", {"rows": len(rows)})

        elif "approved in coupa" in lower or "missing matching oracle invoices" in lower:
            intent = "structured_data"
            tools_called.append("query_po_invoice_matching")
            rows = self.tools.query_missing_oracle_invoice(request.role)
            answer = self._format_table_answer("Approved Coupa POs missing Oracle invoices", rows)
            citations.append(Citation(source="controlled_join", reference="RAW_COUPA_PURCHASE_ORDERS to RAW_ORACLE_AP_INVOICES"))
            self._audit(trace_id, request, intent, "query_po_invoice_matching", {"rows": len(rows)})

        elif match := re.search(r"inv[-\s]?(\d+)", lower):
            intent = "structured_data"
            tools_called.append("query_invoice_exceptions")
            invoice = self.tools.query_invoice_reason(match.group(1), request.role)
            if invoice:
                answer = (
                    f"Invoice {invoice['invoice_number']} is blocked for {invoice['exception_type']}: "
                    f"{invoice['exception_reason']} Recommended action: {invoice['recommended_action']}"
                )
            else:
                answer = "I could not find that invoice in the governed invoice exception mart."
            citations.append(Citation(source="mart", reference="MART_INVOICE_EXCEPTIONS"))
            self._audit(trace_id, request, intent, "query_invoice_exceptions", {"invoice": match.group(1)})

        else:
            intent = "structured_data"
            tools_called.append("query_invoice_exceptions")
            rows = self.tools.query_invoice_exceptions(request.role)
            answer = self._format_table_answer("Top suppliers by blocked invoice amount", rows)
            citations.append(Citation(source="mart", reference="MART_INVOICE_EXCEPTIONS"))
            self._audit(trace_id, request, intent, "query_invoice_exceptions", {"rows": len(rows)})

        latency_ms = int((perf_counter() - started) * 1000)
        self.repo.log_audit(
            trace_id=trace_id,
            user_id=request.user_id,
            role=request.role,
            event_type="chat_completed",
            tool_name=",".join(tools_called),
            details={"intent": intent, "latency_ms": latency_ms},
        )
        return ChatResponse(
            answer=answer,
            intent=intent,
            tools_called=tools_called,
            citations=citations,
            requires_approval=requires_approval,
            draft_id=draft_id,
            trace_id=trace_id,
        )

    def _is_security_denial(self, lower: str) -> bool:
        blocked_phrases = [
            "run this sql",
            "select * from raw",
            "raw supplier bank",
            "bank account",
            "tax id",
            "pretend i am an admin",
            "ignore previous instructions",
            "approve all pending",
        ]
        return any(phrase in lower for phrase in blocked_phrases)

    def _format_policy_answer(self, query: str, matches: list[dict]) -> str:
        if not matches:
            return "I could not find a matching synthetic policy document for that question."
        joined = "\n".join(f"- {match['source']}: {match['excerpt']}" for match in matches)
        if "without receipt" in query.lower():
            prefix = "No. The synthetic matching policy says invoices requiring three-way match should not be paid without receipt confirmation."
        elif "approval" in query.lower():
            prefix = "The synthetic approval matrix requires higher approval as spend increases, with director or executive review for large software purchases."
        else:
            prefix = "The relevant synthetic policy guidance is:"
        return f"{prefix}\n\n{joined}"

    def _format_table_answer(self, title: str, rows: list[dict]) -> str:
        if not rows:
            return f"{title}: no matching records were found."
        lines = [f"{title}:"]
        for idx, row in enumerate(rows[:5], start=1):
            compact = ", ".join(f"{key}={value}" for key, value in row.items())
            lines.append(f"{idx}. {compact}")
        return "\n".join(lines)

    def _audit(
        self,
        trace_id: str,
        request: ChatRequest,
        intent: str,
        tool_name: str | None,
        details: dict,
    ) -> None:
        self.repo.log_audit(
            trace_id=trace_id,
            user_id=request.user_id,
            role=request.role,
            event_type=f"intent:{intent}",
            tool_name=tool_name,
            details=details,
        )
