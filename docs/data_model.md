# Data Model

The project simulates Oracle ERP-style and Coupa-style procurement, payables, supplier, receipt, approval, and payment data.

Core marts:

- `MART_SUPPLIER_360`
- `MART_PROCUREMENT_SPEND`
- `MART_INVOICE_EXCEPTIONS`
- `MART_PO_INVOICE_MATCHING`
- `MART_APPROVAL_BOTTLENECKS`
- `MART_PAYMENT_STATUS`
- `MART_ENTERPRISE_WORKFLOW_HEALTH`

Synthetic data intentionally includes mismatched suppliers, missing receipts, amount variance, pending approvals, overdue invoices, and inconsistent payment terms.
