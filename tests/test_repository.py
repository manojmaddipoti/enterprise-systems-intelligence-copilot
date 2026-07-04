from db.duckdb.repository import Repository


def test_repository_health() -> None:
    health = Repository().health()
    assert health["status"] == "ok"
    assert health["supplier_count"] > 0
    assert health["invoice_count"] > 0


def test_workflow_health_mart_returns_rows() -> None:
    rows = Repository().workflow_health(3)
    assert rows
    assert "workflow_health_score" in rows[0]


def test_no_receipt_percentage() -> None:
    result = Repository().no_receipt_percentage()
    assert result["total_invoices"] > 0
    assert 0 <= result["percentage"] <= 100
