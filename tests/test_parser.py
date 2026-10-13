import pytest

from app.ingestion.parser import DocumentParseError, parse_document


def test_parse_utf8_text() -> None:
    pages = parse_document("guide.txt", "请假需要提前申请。".encode())
    assert pages[0].text == "请假需要提前申请。"


def test_rejects_unsupported_file() -> None:
    with pytest.raises(DocumentParseError):
        parse_document("danger.exe", b"content")

