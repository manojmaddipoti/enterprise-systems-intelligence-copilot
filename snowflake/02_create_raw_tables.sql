USE DATABASE ENTERPRISE_COPILOT_DEV;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE RAW_ORACLE_SUPPLIERS (
  oracle_supplier_id STRING,
  enterprise_supplier_id STRING,
  supplier_name STRING,
  region STRING,
  supplier_tier STRING,
  payment_terms STRING,
  business_unit STRING,
  tax_id STRING,
  bank_account_number STRING,
  status STRING
);

CREATE OR REPLACE TABLE RAW_ORACLE_SUPPLIER_SITES (
  supplier_site_id STRING,
  oracle_supplier_id STRING,
  site_name STRING,
  country STRING,
  payment_terms STRING
);

CREATE OR REPLACE TABLE RAW_ORACLE_PO_HEADERS (
  oracle_po_id STRING,
  po_number STRING,
  oracle_supplier_id STRING,
  business_unit STRING,
  po_amount NUMBER(18,2),
  status STRING,
  created_at TIMESTAMP_NTZ,
  approved_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_ORACLE_PO_LINES (
  oracle_po_line_id STRING,
  oracle_po_id STRING,
  po_number STRING,
  line_number NUMBER,
  description STRING,
  line_amount NUMBER(18,2)
);

CREATE OR REPLACE TABLE RAW_ORACLE_PO_DISTRIBUTIONS (
  po_distribution_id STRING,
  oracle_po_line_id STRING,
  gl_code STRING,
  business_unit STRING,
  amount NUMBER(18,2)
);

CREATE OR REPLACE TABLE RAW_ORACLE_RECEIPTS (
  receipt_id STRING,
  receipt_number STRING,
  po_number STRING,
  received_amount NUMBER(18,2),
  received_at TIMESTAMP_NTZ,
  business_unit STRING
);

CREATE OR REPLACE TABLE RAW_ORACLE_AP_INVOICES (
  invoice_id STRING,
  invoice_number STRING,
  oracle_supplier_id STRING,
  supplier_name STRING,
  business_unit STRING,
  po_number STRING,
  receipt_number STRING,
  invoice_amount NUMBER(18,2),
  open_amount NUMBER(18,2),
  status STRING,
  exception_type STRING,
  exception_reason STRING,
  approval_status STRING,
  owner STRING,
  created_at TIMESTAMP_NTZ,
  due_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_ORACLE_AP_INVOICE_LINES (
  invoice_line_id STRING,
  invoice_id STRING,
  line_number NUMBER,
  description STRING,
  line_amount NUMBER(18,2),
  gl_code STRING
);

CREATE OR REPLACE TABLE RAW_ORACLE_AP_PAYMENTS (
  payment_id STRING,
  invoice_id STRING,
  payment_amount NUMBER(18,2),
  payment_status STRING,
  payment_date TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_ORACLE_GL_CODE_COMBINATIONS (
  gl_code STRING,
  cost_center STRING,
  natural_account STRING
);

CREATE OR REPLACE TABLE RAW_COUPA_SUPPLIERS (
  coupa_supplier_id STRING,
  enterprise_supplier_id STRING,
  supplier_name STRING,
  region STRING,
  commodity STRING,
  payment_terms STRING,
  tax_id STRING,
  status STRING
);

CREATE OR REPLACE TABLE RAW_COUPA_REQUISITIONS (
  requisition_id STRING,
  coupa_supplier_id STRING,
  requester_id STRING,
  business_unit STRING,
  commodity STRING,
  amount NUMBER(18,2),
  status STRING,
  created_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_COUPA_REQUISITION_LINES (
  requisition_line_id STRING,
  requisition_id STRING,
  description STRING,
  quantity NUMBER,
  line_amount NUMBER(18,2)
);

CREATE OR REPLACE TABLE RAW_COUPA_PURCHASE_ORDERS (
  coupa_po_id STRING,
  po_number STRING,
  coupa_supplier_id STRING,
  business_unit STRING,
  commodity STRING,
  po_amount NUMBER(18,2),
  status STRING,
  created_at TIMESTAMP_NTZ,
  approved_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_COUPA_PURCHASE_ORDER_LINES (
  coupa_po_line_id STRING,
  coupa_po_id STRING,
  po_number STRING,
  line_number NUMBER,
  description STRING,
  line_amount NUMBER(18,2)
);

CREATE OR REPLACE TABLE RAW_COUPA_RECEIPTS (
  coupa_receipt_id STRING,
  receipt_number STRING,
  po_number STRING,
  received_amount NUMBER(18,2),
  received_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_COUPA_INVOICES (
  coupa_invoice_id STRING,
  invoice_number STRING,
  coupa_supplier_id STRING,
  supplier_name STRING,
  po_number STRING,
  invoice_amount NUMBER(18,2),
  status STRING,
  created_at TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE RAW_COUPA_APPROVALS (
  approval_event_id STRING,
  approval_chain_id STRING,
  document_id STRING,
  business_unit STRING,
  approver_role STRING,
  approver_name STRING,
  approval_level NUMBER,
  status STRING,
  assigned_at TIMESTAMP_NTZ,
  completed_at TIMESTAMP_NTZ,
  amount NUMBER(18,2)
);

CREATE OR REPLACE TABLE RAW_COUPA_USERS (
  user_id STRING,
  full_name STRING,
  role STRING,
  business_unit STRING,
  personal_email STRING,
  personal_phone STRING
);

CREATE OR REPLACE TABLE RAW_COUPA_COMMODITIES (
  commodity_id STRING,
  commodity_name STRING,
  category STRING
);
