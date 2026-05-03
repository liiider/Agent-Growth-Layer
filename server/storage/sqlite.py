import sqlite3
from pathlib import Path


def initialize_database(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        msg = "Only sqlite:/// database URLs are supported in V0.1."
        raise ValueError(msg)

    database_path = Path(database_url.removeprefix("sqlite:///"))
    if database_path.parent != Path("."):
        database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS guidance_requests (
              id TEXT PRIMARY KEY,
              agent_id TEXT NOT NULL,
              domain TEXT NOT NULL,
              intent TEXT NOT NULL,
              risk_level TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
