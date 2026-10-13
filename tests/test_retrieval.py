from app.models import Chunk
from app.retrieval.hybrid import hashing_embedding, search


def make_chunk(identifier: str, content: str) -> Chunk:
    return Chunk(identifier, "default", "doc", "manual.txt", None, 0, content, hashing_embedding(content))


def test_hybrid_search_returns_relevant_chunk_first() -> None:
    chunks = [
        make_chunk("leave", "员工请病假超过两天需要提交医院证明。"),
        make_chunk("travel", "差旅报销需要提供交通票据。"),
    ]
    hits = search("病假要什么证明", chunks)
    assert hits[0].chunk.id == "leave"

