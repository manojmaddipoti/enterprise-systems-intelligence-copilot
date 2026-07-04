from fastapi import APIRouter

from db.duckdb.repository import Repository

router = APIRouter()


@router.get("/health")
def health() -> dict:
    try:
        return Repository().health()
    except Exception as exc:  # pragma: no cover - surfaced in smoke tests
        return {"status": "not_ready", "detail": str(exc)}
