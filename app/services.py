from __future__ import annotations

from uuid import uuid4

from app.core.config import Settings
from app.generation.answerer import answer_question
from app.ingestion.chunker import chunk_pages
from app.ingestion.parser import parse_document
from app.models import Answer, Chunk, SearchHit
from app.retrieval.hybrid import hashing_embedding, search
from app.storage.repository import KnowledgeRepository


class KnowledgeService:
    def __init__(self, repository: KnowledgeRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def ingest(self, knowledge_base: str, filename: str, data: bytes) -> dict[str, object]:
        if len(data) > self.settings.max_upload_mb * 1024 * 1024:
            raise ValueError(f"文件不能超过 {self.settings.max_upload_mb}MB")
        pages = parse_document(filename, data, max_pages=self.settings.max_pdf_pages)
        total_chars = sum(len(page.text) for page in pages)
        if total_chars > self.settings.max_text_chars:
            raise ValueError("文档提取文字超过安全上限")
        document_id = uuid4().hex
        raw_chunks = chunk_pages(pages, size=self.settings.chunk_size, overlap=self.settings.chunk_overlap)
        chunks = [
            Chunk(
                id=uuid4().hex,
                knowledge_base=knowledge_base,
                document_id=document_id,
                filename=filename,
                page=page,
                position=index,
                content=content,
                embedding=hashing_embedding(content),
            )
            for index, (page, content) in enumerate(raw_chunks)
        ]
        self.repository.add_document(document_id, knowledge_base, filename, len(data), chunks)
        return {"document_id": document_id, "filename": filename, "chunks": len(chunks), "characters": total_chars}

    def retrieve(self, knowledge_base: str, query: str) -> list[SearchHit]:
        return search(query, self.repository.chunks(knowledge_base), top_k=self.settings.retrieval_top_k)

    def ask(self, knowledge_base: str, question: str) -> Answer:
        return answer_question(
            question,
            self.retrieve(knowledge_base, question),
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            model=self.settings.llm_model,
        )

