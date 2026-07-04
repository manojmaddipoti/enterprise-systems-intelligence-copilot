# Architecture

The copilot uses a local-first split architecture.

- Next.js and Vercel AI SDK provide the user-facing product shell and chat experience.
- FastAPI is the controlled enterprise API boundary.
- DuckDB stores synthetic Oracle/Coupa-style data and analytical marts.
- Python agent tools classify intent, query approved marts, search synthetic policies, draft internal actions, mask sensitive fields, and write audit events.
- Snowflake assets mirror the logical model as optional deployment templates.

The default path requires no LLM API key. Rules-based routing keeps demos and evals deterministic.
