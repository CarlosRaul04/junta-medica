"""
SQLiteDatabase: abre conexiones al archivo SQLite y crea las tablas la primera vez.

El SQL es estándar para que pasar a PostgreSQL (AWS RDS) sea solo cambiar esta clase y los stores.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL,
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS consultations (
    consultation_id       INTEGER PRIMARY KEY,
    case_id               TEXT NOT NULL,
    created_at            TEXT NOT NULL,
    user_id               INTEGER NOT NULL REFERENCES users(user_id),
    insufficient_evidence INTEGER NOT NULL,
    primary_icd10         TEXT NOT NULL,
    primary_name          TEXT NOT NULL,
    agreement             REAL NOT NULL,
    rounds                INTEGER NOT NULL,
    severe_alerts         INTEGER NOT NULL,
    traceability          REAL NOT NULL,
    seconds               REAL NOT NULL,
    llm_calls             INTEGER NOT NULL,
    models                TEXT NOT NULL,
    result_key            TEXT NOT NULL,
    report_key            TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_consultations_user ON consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_consultations_case ON consultations(case_id);
"""


class SQLiteDatabase:
    def __init__(self, path: Path):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()
