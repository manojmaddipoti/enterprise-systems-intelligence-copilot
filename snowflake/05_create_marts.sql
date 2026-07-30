USE DATABASE ENTERPRISE_COPILOT_DEV;

CREATE OR REPLACE VIEW MARTS.MART_SUPPLIER_360 AS
SELECT *
FROM MARTS.DT_MART_SUPPLIER_360;

CREATE OR REPLACE VIEW MARTS.MART_PROCUREMENT_SPEND AS
SELECT
  business_unit,
  commodity,
  COUNT(*) AS purchase_order_count,
  SUM(po_amount) AS total_po_amount,
  AVG(po_amount) AS avg_po_amount
FROM RAW.RAW_COUPA_PURCHASE_ORDERS
GROUP BY business_unit, commodity;

CREATE OR REPLACE VIEW MARTS.MART_INVOICE_EXCEPTIONS AS
SELECT *
FROM MARTS.DT_MART_INVOICE_EXCEPTIONS;

CREATE OR REPLACE VIEW MARTS.MART_PO_INVOICE_MATCHING AS
SELECT *
FROM INTEGRATION.DT_INT_PO_INVOICE_MATCH;

CREATE OR REPLACE VIEW MARTS.MART_APPROVAL_BOTTLENECKS AS
SELECT
  approval_chain_id,
  business_unit,
  approver_role,
  approver_name,
  approval_level,
  avg_cycle_time_hours,
  pending_count,
  overdue_count,
  total_amount_pending,
  pending_count * 10 + avg_cycle_time_hours AS bottleneck_score
FROM INTEGRATION.DT_INT_APPROVAL_CYCLE_TIME;

CREATE OR REPLACE VIEW MARTS.MART_PAYMENT_STATUS AS
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
  IFF(i.due_at < CURRENT_TIMESTAMP() AND i.status <> 'PAID', TRUE, FALSE) AS is_overdue
FROM RAW.RAW_ORACLE_AP_INVOICES i
LEFT JOIN RAW.RAW_ORACLE_AP_PAYMENTS p ON i.invoice_id = p.invoice_id;

CREATE OR REPLACE VIEW MARTS.MART_ENTERPRISE_WORKFLOW_HEALTH AS
SELECT *
FROM MARTS.DT_MART_PROCUREMENT_WORKFLOW;
