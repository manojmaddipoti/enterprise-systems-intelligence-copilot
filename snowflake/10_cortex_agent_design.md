# Cortex Agent Design

Suggested tools:

- `structured_data_tool`: Cortex Analyst over the semantic model.
- `policy_search_tool`: Cortex Search over synthetic policy documents.
- `draft_action_tool`: Controlled application function that only creates pending drafts.
- `audit_logger`: Writes traceable app events.

The Snowflake agent should never execute arbitrary user SQL, expose raw tables, approve drafts from prompt text, or bypass masking policies.
