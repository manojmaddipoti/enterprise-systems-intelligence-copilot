from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_admin, routes_audit, routes_chat, routes_drafts, routes_health
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title="Enterprise Systems Intelligence Copilot",
    version="0.1.0",
    description="Governed local-first enterprise AI copilot over synthetic Oracle/Coupa-style data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_chat.router)
app.include_router(routes_admin.router)
app.include_router(routes_audit.router)
app.include_router(routes_drafts.router)
