USE DATABASE ENTERPRISE_COPILOT_DEV;

CREATE OR REPLACE DYNAMIC TABLE STAGING.DT_STG_ORACLE_SUPPLIERS
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  *,
  LOWER(REGEXP_REPLACE(supplier_name, '[^a-zA-Z0-9]', '')) AS supplier_name_normalized
FROM RAW.RAW_ORACLE_SUPPLIERS;

CREATE OR REPLACE DYNAMIC TABLE STAGING.DT_STG_COUPA_SUPPLIERS
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  *,
  LOWER(REGEXP_REPLACE(supplier_name, '[^a-zA-Z0-9]', '')) AS supplier_name_normalized
FROM RAW.RAW_COUPA_SUPPLIERS;

CREATE OR REPLACE DYNAMIC TABLE STAGING.DT_STG_ORACLE_AP_INVOICES
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT *
FROM RAW.RAW_ORACLE_AP_INVOICES;

CREATE OR REPLACE DYNAMIC TABLE STAGING.DT_STG_COUPA_PURCHASE_ORDERS
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT *
FROM RAW.RAW_COUPA_PURCHASE_ORDERS;

CREATE OR REPLACE DYNAMIC TABLE INTEGRATION.DT_INT_SUPPLIER_XREF
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  COALESCE(o.enterprise_supplier_id, c.enterprise_supplier_id) AS enterprise_supplier_id,
  o.oracle_supplier_id,
  c.coupa_supplier_id,
  COALESCE(o.supplier_name, c.supplier_name) AS supplier_name,
  COALESCE(o.region, c.region) AS region,
  o.supplier_tier,
  COALESCE(o.payment_terms, c.payment_terms) AS payment_terms,
  c.commodity,
  CASE
    WHEN o.oracle_supplier_id IS NULL THEN 'COUPA_ONLY'
    WHEN c.coupa_supplier_id IS NULL THEN 'ORACLE_ONLY'
    ELSE 'MATCHED'
  END AS source_alignment
FROM STAGING.DT_STG_ORACLE_SUPPLIERS o
FULL OUTER JOIN STAGING.DT_STG_COUPA_SUPPLIERS c
  ON o.enterprise_supplier_id = c.enterprise_supplier_id;

CREATE OR REPLACE DYNAMIC TABLE INTEGRATION.DT_INT_PO_INVOICE_MATCH
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
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
  IFF(p.po_number IS NOT NULL AND i.po_number IS NOT NULL, TRUE, FALSE) AS has_po_match,
  IFF(r.receipt_number IS NOT NULL AND i.receipt_number IS NOT NULL, TRUE, FALSE) AS has_receipt_match,
  IFF(p.po_number IS NOT NULL AND r.receipt_number IS NOT NULL AND i.invoice_amount <= p.po_amount * 1.05, TRUE, FALSE)
    AS three_way_match_passed
FROM RAW.RAW_ORACLE_AP_INVOICES i
LEFT JOIN RAW.RAW_ORACLE_PO_HEADERS p ON i.po_number = p.po_number
LEFT JOIN RAW.RAW_ORACLE_RECEIPTS r ON i.receipt_number = r.receipt_number;

CREATE OR REPLACE DYNAMIC TABLE INTEGRATION.DT_INT_APPROVAL_CYCLE_TIME
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  approval_chain_id,
  document_id,
  business_unit,
  approver_role,
  approver_name,
  approval_level,
  AVG(DATEDIFF(hour, assigned_at, COALESCE(completed_at, CURRENT_TIMESTAMP()))) AS avg_cycle_time_hours,
  SUM(IFF(status = 'PENDING', 1, 0)) AS pending_count,
  SUM(IFF(status = 'PENDING' AND DATEDIFF(hour, assigned_at, CURRENT_TIMESTAMP()) > 72, 1, 0)) AS overdue_count,
  SUM(IFF(status = 'PENDING', amount, 0)) AS total_amount_pending
FROM RAW.RAW_COUPA_APPROVALS
GROUP BY approval_chain_id, document_id, business_unit, approver_role, approver_name, approval_level;

CREATE OR REPLACE DYNAMIC TABLE MARTS.DT_MART_SUPPLIER_360
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  x.enterprise_supplier_id,
  x.oracle_supplier_id,
  x.coupa_supplier_id,
  x.supplier_name,
  x.region,
  x.supplier_tier,
  x.payment_terms,
  COALESCE(SUM(p.po_amount), 0) AS total_po_amount,
  COALESCE(SUM(i.invoice_amount), 0) AS total_invoice_amount,
  COALESCE(SUM(i.open_amount), 0) AS open_invoice_amount,
  COALESCE(SUM(IFF(i.status = 'PAID', i.invoice_amount, 0)), 0) AS paid_amount,
  COALESCE(SUM(IFF(i.status = 'BLOCKED', 1, 0)), 0) AS exception_count,
  COALESCE(SUM(IFF(i.due_at < CURRENT_TIMESTAMP() AND i.status <> 'PAID', 1, 0)), 0) AS late_payment_count,
  LEAST(100, COALESCE(SUM(IFF(i.status = 'BLOCKED', 1, 0)), 0) * 4) AS risk_score
FROM INTEGRATION.DT_INT_SUPPLIER_XREF x
LEFT JOIN RAW.RAW_ORACLE_PO_HEADERS p ON x.oracle_supplier_id = p.oracle_supplier_id
LEFT JOIN RAW.RAW_ORACLE_AP_INVOICES i ON x.oracle_supplier_id = i.oracle_supplier_id
GROUP BY
  x.enterprise_supplier_id,
  x.oracle_supplier_id,
  x.coupa_supplier_id,
  x.supplier_name,
  x.region,
  x.supplier_tier,
  x.payment_terms;

CREATE OR REPLACE DYNAMIC TABLE MARTS.DT_MART_INVOICE_EXCEPTIONS
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
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
  open_amount AS blocked_invoice_amount,
  DATEDIFF(day, created_at, CURRENT_TIMESTAMP()) AS days_pending,
  po_number,
  receipt_number,
  approval_status,
  owner
FROM RAW.RAW_ORACLE_AP_INVOICES
WHERE status = 'BLOCKED' OR exception_type IS NOT NULL;

CREATE OR REPLACE DYNAMIC TABLE MARTS.DT_MART_PROCUREMENT_WORKFLOW
  TARGET_LAG = '4 hours'
  WAREHOUSE = DEV_XS_WH
AS
SELECT
  p.business_unit,
  TO_VARCHAR(p.created_at, 'YYYY-MM') AS period,
  COUNT(DISTINCT p.po_number) AS total_pos,
  COUNT(DISTINCT i.invoice_id) AS total_invoices,
  SUM(IFF(i.status = 'BLOCKED', 1, 0)) / NULLIF(COUNT(DISTINCT i.invoice_id), 0) AS exception_rate,
  SUM(IFF(m.three_way_match_passed, 1, 0)) / NULLIF(COUNT(DISTINCT i.invoice_id), 0) AS match_rate,
  AVG(COALESCE(a.avg_cycle_time_hours, 0)) / 24 AS avg_approval_cycle_days,
  SUM(IFF(i.status = 'BLOCKED', i.open_amount, 0)) AS blocked_invoice_amount,
  SUM(COALESCE(i.open_amount, 0)) AS open_invoice_amount,
  COUNT(DISTINCT p.coupa_supplier_id) AS supplier_count,
  GREATEST(
    0,
    100
      - COALESCE(SUM(IFF(i.status = 'BLOCKED', 1, 0)) * 100 / NULLIF(COUNT(DISTINCT i.invoice_id), 0), 0)
      - COALESCE(AVG(a.avg_cycle_time_hours) / 24, 0)
  ) AS workflow_health_score
FROM RAW.RAW_COUPA_PURCHASE_ORDERS p
LEFT JOIN RAW.RAW_ORACLE_AP_INVOICES i ON p.po_number = i.po_number
LEFT JOIN INTEGRATION.DT_INT_PO_INVOICE_MATCH m ON i.invoice_id = m.invoice_id
LEFT JOIN INTEGRATION.DT_INT_APPROVAL_CYCLE_TIME a ON p.po_number = a.document_id
GROUP BY p.business_unit, TO_VARCHAR(p.created_at, 'YYYY-MM');
