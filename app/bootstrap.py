from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from app.core.config import get_settings
from data.seed.generate_data import generate
from db.duckdb.init_db import RAW_DIR, init_db
from db.duckdb.repository import Repository

logger = logging.getLogger(__name__)


def bootstrap() -> None:
    settings = get_settings()
    db_path = Path(settings.duckdb_path)

    if _database_is_ready(db_path):
        logger.info("Database is ready at %s; initialization is not required.", db_path)
        return

    if not RAW_DIR.exists() or not any(RAW_DIR.glob("*.csv")):
        logger.info("Synthetic source data is missing; generating it now.")
        generate()

    logger.info("Initializing DuckDB at %s.", db_path)
    init_db()

    if not _database_is_ready(db_path):
        raise RuntimeError(f"Database initialization did not produce a ready database at {db_path}.")


def _database_is_ready(db_path: Path) -> bool:
    if not db_path.exists():
        return False
    try:
        health = Repository(str(db_path)).health()
    except (RuntimeError, duckdb.Error):
        return False
    return health.get("status") == "ok"


if __name__ == "__main__":
    bootstrap()
