from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from app.models import Chunk, SearchHit


TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_PATTERN.findall(text)]


def hashing_embedding(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0 if digest[4] % 2 == 0 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def search(query: str, chunks: list[Chunk], *, top_k: int = 5) -> list[SearchHit]:
    query_tokens = tokenize(query)
    if not query_tokens or not chunks:
        return []
    query_counts = Counter(query_tokens)
    query_vector = hashing_embedding(query)
    document_frequency = Counter(
        token for chunk in chunks for token in set(tokenize(chunk.content))
    )
    total = len(chunks)
    scored: list[SearchHit] = []
    for chunk in chunks:
        counts = Counter(tokenize(chunk.content))
        lexical = sum(
            min(counts[token], count) * math.log((total + 1) / (document_frequency[token] + 0.5))
            for token, count in query_counts.items()
        )
        lexical_normalized = lexical / (lexical + 3.0) if lexical > 0 else 0.0
        semantic = max(0.0, cosine(query_vector, chunk.embedding))
        score = 0.55 * lexical_normalized + 0.45 * semantic
        if score > 0:
            scored.append(SearchHit(chunk, score, lexical_normalized, semantic))
    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

