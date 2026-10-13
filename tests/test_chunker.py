from app.ingestion.chunker import chunk_pages
from app.ingestion.parser import ParsedPage


def test_chunk_pages_keeps_page_number() -> None:
    chunks = chunk_pages([ParsedPage(3, "第一段内容。\n\n第二段内容。")], size=20, overlap=5)
    assert chunks
    assert all(page == 3 for page, _ in chunks)
    assert "第一段" in chunks[0][1]

