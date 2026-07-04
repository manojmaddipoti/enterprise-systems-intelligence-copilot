from fastapi import APIRouter
from pydantic import BaseModel

from db.duckdb.repository import Repository

router = APIRouter()


class FeedbackRequest(BaseModel):
    trace_id: str
    user_id: str = "demo_analyst"
    rating: int
    comment: str = ""


@router.get("/dashboards/workflow-health")
def workflow_health() -> list[dict]:
    return Repository().workflow_health()


@router.get("/dashboards/invoice-exceptions")
def invoice_exceptions() -> list[dict]:
    return Repository().invoice_exceptions()


@router.get("/dashboards/supplier-360/{supplier_id}")
def supplier_360(supplier_id: str) -> dict:
    supplier = Repository().supplier_360(supplier_id)
    return supplier or {"error": "supplier_not_found"}


@router.get("/evals/results")
def eval_results() -> list[dict]:
    return Repository().eval_results()


@router.post("/feedback")
def feedback(request: FeedbackRequest) -> dict:
    return Repository().record_feedback(
        trace_id=request.trace_id,
        user_id=request.user_id,
        rating=request.rating,
        comment=request.comment,
    )
