from pathlib import Path
from types import SimpleNamespace

from app import bootstrap as bootstrap_module


def test_bootstrap_skips_initialization_when_database_is_ready(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "ready.duckdb"
    monkeypatch.setattr(
        bootstrap_module,
        "get_settings",
        lambda: SimpleNamespace(duckdb_path=str(db_path)),
    )
    monkeypatch.setattr(bootstrap_module, "_database_is_ready", lambda path: True)

    generate_called = False
    init_called = False

    def track_generate() -> None:
        nonlocal generate_called
        generate_called = True

    def track_init() -> None:
        nonlocal init_called
        init_called = True

    monkeypatch.setattr(bootstrap_module, "generate", track_generate)
    monkeypatch.setattr(bootstrap_module, "init_db", track_init)

    bootstrap_module.bootstrap()

    assert not generate_called
    assert not init_called


def test_bootstrap_generates_and_initializes_fresh_checkout(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "fresh.duckdb"
    raw_dir = tmp_path / "raw"
    readiness = iter([False, True])
    calls: list[str] = []

    monkeypatch.setattr(
        bootstrap_module,
        "get_settings",
        lambda: SimpleNamespace(duckdb_path=str(db_path)),
    )
    monkeypatch.setattr(bootstrap_module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(
        bootstrap_module,
        "_database_is_ready",
        lambda path: next(readiness),
    )
    monkeypatch.setattr(bootstrap_module, "generate", lambda: calls.append("generate"))
    monkeypatch.setattr(bootstrap_module, "init_db", lambda: calls.append("init_db"))

    bootstrap_module.bootstrap()

    assert calls == ["generate", "init_db"]
