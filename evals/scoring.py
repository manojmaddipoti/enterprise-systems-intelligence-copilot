from __future__ import annotations

from app.schemas.chat import ChatResponse


def score_case(case: dict, response: ChatResponse) -> dict:
    answer_lower = response.answer.lower()
    must_contain = [item.lower() for item in case.get("must_contain", [])]
    must_not_contain = [item.lower() for item in case.get("must_not_contain", [])]
    expected_tools = set(case.get("expected_tools", []))
    actual_tools = set(response.tools_called)

    checks = {
        "intent": response.intent == case.get("expected_intent"),
        "tools": expected_tools.issubset(actual_tools),
        "must_contain": all(item in answer_lower for item in must_contain),
        "must_not_contain": all(item not in answer_lower for item in must_not_contain),
    }
    return {"passed": all(checks.values()), "checks": checks}
