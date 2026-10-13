from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.ingestion.parser import DocumentParseError
from app.services import KnowledgeService
from app.storage.repository import KnowledgeRepository


class QuestionRequest(BaseModel):
    knowledge_base: str = Field(default="default", min_length=1, max_length=80)
    question: str = Field(min_length=2, max_length=2_000)


def create_app() -> FastAPI:
    settings = get_settings()
    service = KnowledgeService(KnowledgeRepository(settings.database_path), settings)
    app = FastAPI(title="Knowledge Agent API", description="Citation-grounded knowledge base RAG API", version="0.2.0")

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "knowledge-agent"}

    @app.get("/api/documents", tags=["knowledge"])
    async def documents(knowledge_base: str = "default") -> list[dict[str, object]]:
        return service.repository.list_documents(knowledge_base)

    @app.post("/api/documents", status_code=201, tags=["knowledge"])
    async def upload_document(knowledge_base: str = Form("default"), file: UploadFile = File(...)) -> dict[str, object]:
        if not file.filename:
            raise HTTPException(400, "缺少文件名")
        data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        try:
            return service.ingest(knowledge_base.strip() or "default", file.filename, data)
        except (ValueError, DocumentParseError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.delete("/api/documents/{document_id}", tags=["knowledge"])
    async def delete_document(document_id: str) -> dict[str, bool]:
        if not service.repository.delete_document(document_id):
            raise HTTPException(404, "文档不存在")
        return {"deleted": True}

    @app.post("/api/ask", tags=["chat"])
    async def ask(payload: QuestionRequest) -> dict[str, object]:
        return asdict(service.ask(payload.knowledge_base, payload.question))

    app.state.knowledge_service = service
    return app


app = create_app()
