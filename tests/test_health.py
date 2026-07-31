from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_does_not_require_database_access() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
