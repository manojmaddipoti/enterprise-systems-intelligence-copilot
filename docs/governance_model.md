# Governance Model

Governance is enforced in backend code.

- Users cannot run arbitrary SQL.
- Agent tools query approved marts or controlled joins only.
- Sensitive fields are masked unless the role explicitly allows full access.
- Prompt text cannot elevate roles.
- Draft actions are internal records and require manager or admin approval.
- Audit events are written for chat turns, tool calls, denials, drafts, and evals.

Roles:

- `APP_ANALYST`
- `APP_MANAGER`
- `APP_ADMIN`
- `APP_AUDITOR`
