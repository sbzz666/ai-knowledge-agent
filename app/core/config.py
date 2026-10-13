from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "Knowledge Agent"
    app_env: str = "development"
    database_path: Path = Path("data/knowledge.db")
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    max_upload_mb: int = 10
    max_pdf_pages: int = 80
    max_text_chars: int = 300_000
    chunk_size: int = 700
    chunk_overlap: int = 120
    retrieval_top_k: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Knowledge Agent"),
        app_env=os.getenv("APP_ENV", "development"),
        database_path=Path(os.getenv("DATABASE_PATH", "data/knowledge.db")),
        llm_base_url=os.getenv("LLM_BASE_URL") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
        max_pdf_pages=int(os.getenv("MAX_PDF_PAGES", "80")),
        max_text_chars=int(os.getenv("MAX_TEXT_CHARS", "300000")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "700")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
    )
