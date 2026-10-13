from __future__ import annotations

import re

from app.ingestion.parser import ParsedPage


def chunk_pages(pages: list[ParsedPage], *, size: int = 700, overlap: int = 120) -> list[tuple[int | None, str]]:
    if size <= overlap or overlap < 0:
        raise ValueError("chunk size 必须大于 overlap")
    chunks: list[tuple[int | None, str]] = []
    for page in pages:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", page.text) if part.strip()]
        buffer = ""
        for paragraph in paragraphs:
            if len(buffer) + len(paragraph) + 1 <= size:
                buffer = f"{buffer}\n{paragraph}".strip()
                continue
            if buffer:
                chunks.append((page.page, buffer))
            while len(paragraph) > size:
                chunks.append((page.page, paragraph[:size]))
                paragraph = paragraph[size - overlap :]
            buffer = paragraph
        if buffer:
            chunks.append((page.page, buffer))
    return chunks

