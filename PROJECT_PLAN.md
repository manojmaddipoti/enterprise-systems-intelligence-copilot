# Project Plan: Enterprise Systems Intelligence Copilot With Vercel AI SDK

## Summary

Build a local-first enterprise AI copilot using Next.js, React, TypeScript, and Vercel AI SDK for the product UI and chat experience, with FastAPI and DuckDB as the governed enterprise data backend. The default demo is mock/rules-based so it runs without paid LLM keys.

## Key Decisions

- Use `web/` for the Next.js application and Vercel AI SDK chat UI.
- Use `app/`, `agents/`, `db/`, `data/`, and `evals/` for the Python backend, governed tools, DuckDB data layer, synthetic data, and evaluations.
- Keep DuckDB as the required MVP backend; treat Postgres as a stretch goal.
- Keep Snowflake assets optional and template-based under `snowflake/`.
- Do not include proprietary workplace code, schema, data, screenshots, URLs, access rules, or business logic.

## Milestones

1. Repo foundation: scaffold Python backend, Next.js frontend, shared env examples, Makefile, Docker assets, and README.
2. Synthetic data: deterministic Faker-based Oracle-like, Coupa-like, app, and policy datasets.
3. DuckDB local database: raw tables, app tables, marts, and validation checks.
4. FastAPI backend: health, chat, dashboards, drafts, audit, evals, and feedback endpoints.
5. Agent layer: rules-based router, governed query tools, policy search, draft actions, masking, permissions, and audit events.
6. Next.js frontend: Vercel AI SDK chat page, workflow dashboard, invoice exceptions, supplier 360, draft approvals, audit log, and eval results.
7. Tests and evals: unit tests, security tests, JSONL eval runner, and scorecard.
8. Snowflake assets: optional Dynamic Tables, semantic YAML, Cortex design notes, masking, row access, and demo queries.
9. Documentation polish: architecture, data model, governance model, Snowflake deployment, and demo script.

## Public Interfaces

FastAPI is the controlled enterprise API layer:

- `GET /health`
- `POST /chat`
- `GET /audit/events`
- `GET /drafts`
- `POST /drafts/{draft_id}/approve`
- `POST /drafts/{draft_id}/reject`
- `GET /dashboards/workflow-health`
- `GET /dashboards/invoice-exceptions`
- `GET /dashboards/supplier-360/{supplier_id}`
- `GET /evals/results`
- `POST /feedback`

The Next.js app calls these APIs and uses Vercel AI SDK for chat state and streaming-compatible UI.

## Test Plan

- Backend unit tests for data generation, repository queries, governed tools, permissions, masking, and draft workflow.
- API smoke tests for all FastAPI routes.
- Frontend smoke tests for core pages and chat rendering.
- Security tests for prompt injection, raw SQL denial, role escalation denial, and sensitive-field masking.
- Eval suite for structured questions, policy questions, mixed data-policy questions, and tool routing.

Acceptance targets:

- Local app runs without LLM API keys.
- Tool routing accuracy >= 90%.
- Sensitive data leakage: 0 known failures.
- Unauthorized action execution: 0 known failures.
- Structured Q&A correctness >= 85%.
- Policy grounding correctness >= 90%.

## Assumptions

- Use Next.js + Vercel AI SDK + FastAPI as the default architecture.
- Add real LLM providers as optional configuration, not required for MVP.
- Snowflake remains optional and account-specific values must be supplied by the user.
- All datasets, policies, roles, schemas, screenshots, and examples are synthetic and generic.
