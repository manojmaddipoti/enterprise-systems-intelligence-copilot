# Snowflake Deployment

The `snowflake/` directory contains optional SQL/YAML templates for a Snowflake version of the same logical model.

The assets are intentionally generic. Supply account-specific values, stages, warehouses, users, and integration settings before execution.

Suggested order:

1. Cost controls.
2. Database, schemas, and roles.
3. Raw tables.
4. Data loading templates.
5. Dynamic Tables or fallback marts.
6. Masking and row access policies.
7. Semantic model.
8. Cortex Search and Cortex Agent design.
9. Demo queries.
