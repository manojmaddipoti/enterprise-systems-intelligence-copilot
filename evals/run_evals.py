from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from agents.orchestrator import Orchestrator
from app.schemas.chat import ChatRequest
from db.duckdb.repository import Repository
from evals.scoring import score_case

DATASET_DIR = Path("evals/datasets")
REPORT_PATH = Path("evals/eval_report.md")


def _load_cases() -> list[dict]:
    cases: list[dict] = []
    for path in sorted(DATASET_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                case = json.loads(line)
                case["dataset"] = path.name
                cases.append(case)
    return cases


def run() -> dict:
    repo = Repository()
    agent = Orchestrator(repo)
    run_id = f"EVAL-{uuid.uuid4().hex[:8].upper()}"
    results = []
    for case in _load_cases():
        started = time.perf_counter()
        response = agent.handle(
            ChatRequest(user_id="eval_user", role="APP_ANALYST", message=case["input"])
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        score = score_case(case, response)
        repo.store_eval_result(
            run_id=run_id,
            eval_id=case["id"],
            passed=score["passed"],
            intent=response.intent,
            tools_called=response.tools_called,
            latency_ms=latency_ms,
        )
        results.append({**case, **score, "response": response.model_dump(), "latency_ms": latency_ms})

    passed = sum(1 for item in results if item["passed"])
    summary = {
        "run_id": run_id,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed * 100 / max(len(results), 1), 2),
    }
    _write_report(summary, results)
    print(json.dumps(summary, indent=2))
    return summary


def _write_report(summary: dict, results: list[dict]) -> None:
    lines = [
        "# Eval Report",
        "",
        f"- Run ID: {summary['run_id']}",
        f"- Total: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Pass rate: {summary['pass_rate']}%",
        "",
        "## Cases",
    ]
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"- {status} `{result['id']}` ({result['dataset']}): {result['input']}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
