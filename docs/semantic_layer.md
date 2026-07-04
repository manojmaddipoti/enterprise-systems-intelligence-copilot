# Semantic Layer

The local semantic layer maps business terms to governed marts and fixed tool routes.

Examples:

- Supplier, vendor, and provider map to supplier analysis.
- Bill and AP invoice map to invoice analysis.
- Hold, blocked invoice, and issue map to exception analysis.
- Approval delay, bottleneck, and pending time map to approval cycle analysis.

The local router is deterministic for MVP. Real LLM providers can be added later without changing the governed tool contracts.
