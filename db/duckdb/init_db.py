from __future__ import annotations

from pathlib import Path

import duckdb

from app.core.config import get_settings

RAW_DIR = Path("data/raw")
MARTS_SQL = Path("db/duckdb/marts.sql")


def init_db() -> None:
    settings = get_settings()
    db_path = Path(settings.duckdb_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.csv")):
        raise SystemExit("No raw data found. Run `make seed` first.")

    con = duckdb.connect(str(db_path))
    for csv_file in RAW_DIR.glob("*.csv"):
        table_name = csv_file.stem
        read_options = "header=true, all_varchar=true" if table_name == "RAW_COUPA_APPROVALS" else "header=true"
        con.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto(?, {read_options})",
            [str(csv_file)],
        )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS APP_DRAFT_ACTIONS (
          draft_id VARCHAR PRIMARY KEY,
          draft_type VARCHAR,
          title VARCHAR,
          body VARCHAR,
          status VARCHAR,
          created_by VARCHAR,
          approved_by VARCHAR,
          created_at TIMESTAMP,
          updated_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS APP_AUDIT_EVENTS (
          event_id VARCHAR PRIMARY KEY,
          trace_id VARCHAR,
          user_id VARCHAR,
          role VARCHAR,
          event_type VARCHAR,
          tool_name VARCHAR,
          details JSON,
          created_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS APP_AGENT_FEEDBACK (
          feedback_id VARCHAR PRIMARY KEY,
          trace_id VARCHAR,
          user_id VARCHAR,
          rating INTEGER,
          comment VARCHAR,
          created_at TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS APP_EVAL_RESULTS (
          run_id VARCHAR,
          eval_id VARCHAR,
          passed BOOLEAN,
          intent VARCHAR,
          tools_called VARCHAR,
          latency_ms INTEGER,
          created_at TIMESTAMP
        )
        """
    )
    con.execute(MARTS_SQL.read_text(encoding="utf-8"))
    tables = con.execute("SHOW TABLES").fetchall()
    con.close()
    print(f"Initialized {db_path} with {len(tables)} tables/views.")


if __name__ == "__main__":
    init_db()
