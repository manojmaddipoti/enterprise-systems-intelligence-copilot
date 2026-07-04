CREATE OR REPLACE VIEW MART_SUPPLIER_360 AS
WITH invoice_rollup AS (
  SELECT
    oracle_supplier_id,
    SUM(invoice_amount) AS total_invoice_amount,
    SUM(open_amount) AS open_invoice_amount,
    SUM(CASE WHEN status = 'PAID' THEN invoice_amount ELSE 0 END) AS paid_amount,
    SUM(CASE WHEN status = 'BLOCKED' THEN 1 ELSE 0 END) AS exception_count,
    SUM(CASE WHEN due_at < now() AND status <> 'PAID' THEN 1 ELSE 0 END) AS late_payment_count
  FROM RAW_ORACLE_AP_INVOICES
  GROUP BY oracle_supplier_id
),
po_rollup AS (
  SELECT oracle_supplier_id, SUM(po_amount) AS total_po_amount
  FROM RAW_ORACLE_PO_HEADERS
  GROUP BY oracle_supplier_id
),
approval_rollup AS (
  SELECT
    document_id,
    AVG(CASE
      WHEN completed_at IS NULL OR completed_at = '' THEN NULL
      ELSE date_diff('hour', CAST(assigned_at AS TIMESTAMP), try_cast(NULLIF(completed_at, '') AS TIMESTAMP)) / 24.0
    END) AS avg_approval_cycle_days
  FROM RAW_COUPA_APPROVALS
  GROUP BY document_id
),
supplier_approval AS (
  SELECT p.oracle_supplier_id, AVG(a.avg_approval_cycle_days) AS avg_approval_cycle_days
  FROM RAW_ORACLE_PO_HEADERS p
  LEFT JOIN approval_rollup a ON p.po_number = a.document_id
  GROUP BY p.oracle_supplier_id
)
SELECT
  o.enterprise_supplier_id,
  o.oracle_supplier_id,
  c.coupa_supplier_id,
  o.supplier_name,
  lower(regexp_replace(o.supplier_name, '[^a-zA-Z0-9]', '', 'g')) AS supplier_name_normalized,
  o.region,
  o.supplier_tier,
  o.payment_terms,
  COALESCE(p.total_po_amount, 0) AS total_po_amount,
  COALESCE(i.total_invoice_amount, 0) AS total_invoice_amount,
  COALESCE(i.open_invoice_amount, 0) AS open_invoice_amount,
  COALESCE(i.paid_amount, 0) AS paid_amount,
  COALESCE(i.exception_count, 0) AS exception_count,
  COALESCE(i.late_payment_count, 0) AS late_payment_count,
  COALESCE(sa.avg_approval_cycle_days, 0) AS avg_approval_cycle_days,
  LEAST(100, COALESCE(i.exception_count, 0) * 4 + COALESCE(i.late_payment_count, 0) * 3) AS risk_score
FROM RAW_ORACLE_SUPPLIERS o
LEFT JOIN RAW_COUPA_SUPPLIERS c ON o.enterprise_supplier_id = c.enterprise_supplier_id
LEFT JOIN po_rollup p ON o.oracle_supplier_id = p.oracle_supplier_id
LEFT JOIN invoice_rollup i ON o.oracle_supplier_id = i.oracle_supplier_id
LEFT JOIN supplier_approval sa ON o.oracle_supplier_id = sa.oracle_supplier_id;

CREATE OR REPLACE VIEW MART_INVOICE_EXCEPTIONS AS
SELECT
  'EXC-' || invoice_id AS exception_id,
  invoice_id,
  invoice_number,
  oracle_supplier_id AS supplier_id,
  supplier_name,
  business_unit,
  exception_type,
  exception_reason,
  invoice_amount,
  open_amount,
  date_diff('day', CAST(created_at AS TIMESTAMP), now()) AS days_pending,
  po_number,
  receipt_number,
  approval_status,
  owner,
  CASE
    WHEN exception_type = 'NO_RECEIPT' THEN 'Request receipt confirmation from receiving team.'
    WHEN exception_type = 'AMOUNT_VARIANCE' THEN 'Review variance against PO and receipt tolerance.'
    WHEN exception_type = 'MISSING_APPROVAL' THEN 'Escalate pending approval chain.'
    WHEN exception_type = 'NO_PO_MATCH' THEN 'Request PO reference or non-PO approval.'
    WHEN exception_type = 'SUPPLIER_MISMATCH' THEN 'Review supplier cross-reference before release.'
    ELSE 'Review invoice status.'
  END AS recommended_action
FROM RAW_ORACLE_AP_INVOICES
WHERE status = 'BLOCKED' OR exception_type <> '';

CREATE OR REPLACE VIEW MART_PO_INVOICE_MATCHING AS
SELECT
  i.invoice_id,
  i.invoice_number,
  i.supplier_name,
  i.business_unit,
  i.po_number,
  i.receipt_number,
  i.invoice_amount,
  p.po_amount,
  r.received_amount,
  CASE WHEN p.po_number IS NULL OR i.po_number = '' THEN FALSE ELSE TRUE END AS has_po_match,
  CASE WHEN r.receipt_number IS NULL OR i.receipt_number = '' THEN FALSE ELSE TRUE END AS has_receipt_match,
  CASE WHEN p.po_number IS NOT NULL AND r.receipt_number IS NOT NULL AND i.invoice_amount <= p.po_amount * 1.05 THEN TRUE ELSE FALSE END AS three_way_match_passed
FROM RAW_ORACLE_AP_INVOICES i
LEFT JOIN RAW_ORACLE_PO_HEADERS p ON i.po_number = p.po_number
LEFT JOIN RAW_ORACLE_RECEIPTS r ON i.receipt_number = r.receipt_number;

CREATE OR REPLACE VIEW MART_APPROVAL_BOTTLENECKS AS
WITH normalized AS (
  SELECT
    approval_chain_id,
    business_unit,
    approver_role,
    approver_name,
    approval_level,
    status,
    try_cast(amount AS DOUBLE) AS amount,
    try_cast(assigned_at AS TIMESTAMP) AS assigned_ts,
    COALESCE(try_cast(NULLIF(completed_at, '') AS TIMESTAMP), now()) AS completed_ts
  FROM RAW_COUPA_APPROVALS
)
SELECT
  approval_chain_id,
  business_unit,
  approver_role,
  approver_name,
  approval_level,
  AVG(date_diff('hour', assigned_ts, completed_ts)) AS avg_cycle_time_hours,
  SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
  SUM(CASE WHEN status = 'PENDING' AND date_diff('hour', assigned_ts, now()) > 72 THEN 1 ELSE 0 END) AS overdue_count,
  SUM(CASE WHEN status = 'PENDING' THEN amount ELSE 0 END) AS total_amount_pending,
  SUM(CASE WHEN status = 'PENDING' THEN 10 ELSE 0 END) + AVG(date_diff('hour', assigned_ts, completed_ts)) AS bottleneck_score
FROM normalized
GROUP BY approval_chain_id, business_unit, approver_role, approver_name, approval_level;

CREATE OR REPLACE VIEW MART_PAYMENT_STATUS AS
SELECT
  i.invoice_id,
  i.invoice_number,
  i.supplier_name,
  i.business_unit,
  i.invoice_amount,
  i.open_amount,
  i.status AS invoice_status,
  p.payment_id,
  COALESCE(p.payment_status, 'UNPAID') AS payment_status,
  p.payment_date,
  i.due_at,
  CASE WHEN i.due_at < now() AND i.status <> 'PAID' THEN TRUE ELSE FALSE END AS is_overdue
FROM RAW_ORACLE_AP_INVOICES i
LEFT JOIN RAW_ORACLE_AP_PAYMENTS p ON i.invoice_id = p.invoice_id;

CREATE OR REPLACE VIEW MART_PROCUREMENT_SPEND AS
SELECT
  business_unit,
  commodity,
  COUNT(*) AS purchase_order_count,
  SUM(po_amount) AS total_po_amount,
  AVG(po_amount) AS avg_po_amount
FROM RAW_COUPA_PURCHASE_ORDERS
GROUP BY business_unit, commodity;

CREATE OR REPLACE VIEW MART_ENTERPRISE_WORKFLOW_HEALTH AS
SELECT
  p.business_unit,
  strftime(CAST(p.created_at AS TIMESTAMP), '%Y-%m') AS period,
  COUNT(DISTINCT p.po_number) AS total_pos,
  COUNT(DISTINCT i.invoice_id) AS total_invoices,
  SUM(CASE WHEN i.status = 'BLOCKED' THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(DISTINCT i.invoice_id), 0) AS exception_rate,
  SUM(CASE WHEN m.three_way_match_passed THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(DISTINCT i.invoice_id), 0) AS match_rate,
  AVG(COALESCE(a.avg_cycle_time_hours, 0)) / 24.0 AS avg_approval_cycle_days,
  SUM(CASE WHEN i.status = 'BLOCKED' THEN i.open_amount ELSE 0 END) AS blocked_invoice_amount,
  SUM(COALESCE(i.open_amount, 0)) AS open_invoice_amount,
  COUNT(DISTINCT p.coupa_supplier_id) AS supplier_count,
  GREATEST(
    0,
    100
      - COALESCE(SUM(CASE WHEN i.status = 'BLOCKED' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(DISTINCT i.invoice_id), 0), 0)
      - COALESCE(AVG(a.avg_cycle_time_hours) / 24.0, 0)
  ) AS workflow_health_score
FROM RAW_COUPA_PURCHASE_ORDERS p
LEFT JOIN RAW_ORACLE_AP_INVOICES i ON p.po_number = i.po_number
LEFT JOIN MART_PO_INVOICE_MATCHING m ON i.invoice_id = m.invoice_id
LEFT JOIN MART_APPROVAL_BOTTLENECKS a ON p.po_number LIKE replace(a.approval_chain_id, 'APR-CHAIN-', 'PO-')
GROUP BY p.business_unit, strftime(CAST(p.created_at AS TIMESTAMP), '%Y-%m');
