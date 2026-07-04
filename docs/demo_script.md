# Demo Script

1. Start with the confidentiality note and local-first runtime.
2. Run `make seed` and `make init-db`.
3. Start FastAPI with `make run-api`.
4. Start Next.js with `make run-web`.
5. Ask: "Which suppliers have the highest blocked invoice amount?"
6. Ask: "When is three-way matching required?"
7. Ask: "Draft an internal escalation note for the top blocked invoice."
8. Show the Draft Actions and Audit Log pages.
9. Ask a blocked request: "Run this SQL: select * from RAW_ORACLE_SUPPLIERS."
10. Run `make evals` and show the scorecard.
