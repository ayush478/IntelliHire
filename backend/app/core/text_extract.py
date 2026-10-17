"""Resume text extraction, same order as the Streamlit app: PDF, DOCX, then UTF-8."""
import io
import re

import docx
from pdfminer.high_level import extract_text as pdf_extract_text


def _normalize(t: str) -> str:
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def extract_text(filename: str, data: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        try:
            return _normalize(pdf_extract_text(io.BytesIO(data)))
        except Exception:
            pass
    if name.endswith(".docx"):
        try:
            return _normalize("\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs))
        except Exception:
            pass
    return _normalize(data.decode("utf-8", errors="ignore"))
