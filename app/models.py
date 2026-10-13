from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Chunk:
    id: str
    knowledge_base: str
    document_id: str
    filename: str
    page: int | None
    position: int
    content: str
    embedding: list[float]


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float
    lexical_score: float
    semantic_score: float


@dataclass(frozen=True)
class Citation:
    source: str
    page: int | None
    chunk_id: str
    quote: str
    score: float


@dataclass(frozen=True)
class Answer:
    text: str
    citations: list[Citation]
    grounded: bool
    created_at: str = datetime.now(timezone.utc).isoformat()

