from fastapi import APIRouter, HTTPException, status

from db.duckdb.repository import Repository

router = APIRouter()


@router.get("/health/live")
def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness() -> dict:
    try:
        return Repository().health()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database is not ready: {exc}",
        ) from exc


@router.get("/health")
def health() -> dict:
    return readiness()
