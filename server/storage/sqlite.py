import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml


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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS experiences (
              id TEXT PRIMARY KEY,
              agent_id TEXT NOT NULL,
              domain TEXT NOT NULL,
              intent TEXT NOT NULL,
              user_input TEXT NOT NULL,
              agent_output TEXT NOT NULL,
              tools_used TEXT NOT NULL,
              retrieved_context TEXT NOT NULL,
              feedback TEXT,
              result_status TEXT NOT NULL,
              risk_level TEXT NOT NULL,
              extraction_status TEXT NOT NULL,
              metadata TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cognitions (
              id TEXT PRIMARY KEY,
              experience_id TEXT NOT NULL,
              type TEXT NOT NULL,
              content TEXT NOT NULL,
              agent_id TEXT NOT NULL,
              domain TEXT NOT NULL,
              intent TEXT NOT NULL,
              confidence REAL NOT NULL,
              risk_level TEXT NOT NULL,
              weight TEXT NOT NULL,
              status TEXT NOT NULL,
              evidence_refs TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY(experience_id) REFERENCES experiences(id)
            )
            """
        )


def sqlite_path_from_url(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        msg = "Only sqlite:/// database URLs are supported."
        raise ValueError(msg)
    return Path(database_url.removeprefix("sqlite:///"))


@contextmanager
def connect(database_url: str) -> Iterator[sqlite3.Connection]:
    database_path = sqlite_path_from_url(database_url)
    if database_path.parent != Path("."):
        database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def encode_json(value: Any) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False)


def decode_json(value: str) -> Any:
    return yaml.safe_load(value) if value else None
