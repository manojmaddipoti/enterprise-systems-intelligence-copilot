USE DATABASE ENTERPRISE_COPILOT_DEV;

CREATE OR REPLACE TABLE SEMANTIC.POLICY_DOCUMENTS (
  document_id STRING,
  document_name STRING,
  document_text STRING
);

-- Template only. Configure Cortex Search after loading synthetic policy docs.
-- CREATE CORTEX SEARCH SERVICE SEMANTIC.POLICY_SEARCH
--   ON document_text
--   WAREHOUSE = DEV_XS_WH
--   TARGET_LAG = '24 hours'
--   AS SELECT document_id, document_name, document_text FROM SEMANTIC.POLICY_DOCUMENTS;
