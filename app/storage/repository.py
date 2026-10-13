from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.models import Chunk


class KnowledgeRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    knowledge_base TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    knowledge_base TEXT NOT NULL,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    filename TEXT NOT NULL,
                    page INTEGER,
                    position INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_chunks_kb ON chunks(knowledge_base);
                """
            )

    def add_document(self, document_id: str, knowledge_base: str, filename: str, size: int, chunks: list[Chunk]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO documents(id, knowledge_base, filename, size_bytes) VALUES (?, ?, ?, ?)",
                (document_id, knowledge_base, filename, size),
            )
            connection.executemany(
                """INSERT INTO chunks(id, knowledge_base, document_id, filename, page, position, content, embedding)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        chunk.id, chunk.knowledge_base, chunk.document_id, chunk.filename,
                        chunk.page, chunk.position, chunk.content, json.dumps(chunk.embedding),
                    )
                    for chunk in chunks
                ],
            )

    def chunks(self, knowledge_base: str) -> list[Chunk]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM chunks WHERE knowledge_base = ? ORDER BY filename, position",
                (knowledge_base,),
            ).fetchall()
        return [
            Chunk(
                id=row["id"], knowledge_base=row["knowledge_base"], document_id=row["document_id"],
                filename=row["filename"], page=row["page"], position=row["position"],
                content=row["content"], embedding=json.loads(row["embedding"]),
            )
            for row in rows
        ]

    def list_documents(self, knowledge_base: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, filename, size_bytes, created_at FROM documents WHERE knowledge_base = ? ORDER BY created_at DESC",
                (knowledge_base,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_document(self, document_id: str) -> bool:
        with self._connect() as connection:
            connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            cursor = connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return cursor.rowcount > 0

