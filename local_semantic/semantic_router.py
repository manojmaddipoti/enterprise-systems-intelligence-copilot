INTENT_PATTERNS = {
    "query_invoice_exceptions": ["blocked invoice", "highest blocked", "exception patterns"],
    "query_approval_bottlenecks": ["slowest approval", "approval cycle", "bottleneck"],
    "query_po_invoice_matching": ["no matching receipt", "missing matching oracle invoices"],
    "search_policy_documents": ["policy", "three-way", "approval level"],
    "create_draft_action": ["draft", "escalation"],
    "deny": ["run sql", "bank account", "pretend i am an admin"],
}


def route(message: str) -> str:
    lower = message.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in lower for pattern in patterns):
            return intent
    return "query_invoice_exceptions"
