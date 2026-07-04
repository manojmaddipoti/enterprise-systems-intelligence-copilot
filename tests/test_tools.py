from agents.orchestrator import Orchestrator
from app.schemas.chat import ChatRequest


def test_structured_prompt_routes_to_invoice_tool() -> None:
    response = Orchestrator().handle(
        ChatRequest(message="Which suppliers have the highest blocked invoice amount?")
    )
    assert response.intent == "structured_data"
    assert "query_invoice_exceptions" in response.tools_called
    assert "blocked" in response.answer.lower()


def test_policy_prompt_routes_to_policy_tool() -> None:
    response = Orchestrator().handle(ChatRequest(message="When is three-way matching required?"))
    assert response.intent == "policy_lookup"
    assert "search_policy_documents" in response.tools_called
    assert "three-way" in response.answer.lower()


def test_draft_creation_requires_approval() -> None:
    response = Orchestrator().handle(
        ChatRequest(message="Draft an internal escalation note for the top blocked invoice.")
    )
    assert response.intent == "action_drafting"
    assert response.requires_approval is True
    assert response.draft_id is not None
