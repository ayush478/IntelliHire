"""Run from backend/:  python -m tests.test_extract_and_usage   (or pytest)"""
import io

import docx

from app.core.text_extract import extract_text
from app.core.usage import calls, record


def test_extract_text():
    d = docx.Document()
    d.add_paragraph("Senior Engineer")
    d.add_paragraph("Built  Kafka pipelines")
    buf = io.BytesIO()
    d.save(buf)
    assert extract_text("cv.DOCX", buf.getvalue()) == "Senior Engineer Built Kafka pipelines"
    assert extract_text("cv.txt", b"plain   text\n") == "plain text"
    # a corrupt PDF falls back to UTF-8 instead of raising
    assert extract_text("cv.pdf", b"not really a pdf") == "not really a pdf"


def test_usage_counter():
    calls.clear()
    record("gemini_parse_resume")
    record("gemini_parse_resume")
    record("gemini_ai_detect")
    assert dict(calls) == {"gemini_parse_resume": 2, "gemini_ai_detect": 1}


if __name__ == "__main__":
    test_extract_text()
    test_usage_counter()
    print("ok")
