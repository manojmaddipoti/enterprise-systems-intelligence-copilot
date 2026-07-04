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
