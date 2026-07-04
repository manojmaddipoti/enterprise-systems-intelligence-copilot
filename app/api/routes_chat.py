from fastapi import APIRouter

from agents.orchestrator import Orchestrator
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return Orchestrator().handle(request)
