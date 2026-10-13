from pathlib import Path

from app.core.config import Settings
from app.services import KnowledgeService
from app.storage.repository import KnowledgeRepository


def test_ingest_and_offline_answer(tmp_path: Path) -> None:
    settings = Settings(database_path=tmp_path / "test.db")
    service = KnowledgeService(KnowledgeRepository(settings.database_path), settings)
    result = service.ingest("company", "rules.txt", "病假超过两天需要医院证明。".encode())
    answer = service.ask("company", "病假需要什么证明？")
    assert result["chunks"] == 1
    assert answer.grounded is True
    assert answer.citations[0].source == "rules.txt"

