USE DATABASE ENTERPRISE_COPILOT_DEV;

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
  DATEDIFF(day, created_at, CURRENT_TIMESTAMP()) AS days_pending,
  po_number,
  receipt_number,
  approval_status,
  owner
FROM RAW.RAW_ORACLE_AP_INVOICES
WHERE status = 'BLOCKED' OR exception_type IS NOT NULL;
