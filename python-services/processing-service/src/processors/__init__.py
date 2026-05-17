# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Text extraction and chunking helpers for supported document formats.

Supports PDF (via pdfplumber), PPTX/PPT (via python-pptx), and plain TXT.
Text is split into token-bounded chunks using OpenAI's tiktoken tokeniser so
that each chunk fits within a single LLM context window slot.
"""
import logging

import pdfplumber
import tiktoken
from pptx import Presentation

logger = logging.getLogger(__name__)

_ENCODING = "cl100k_base"
_CHUNK_TOKENS = 512


def extract_text(file_url: str, file_type: str) -> tuple:
    """Extract full text and page count from a document file.

    Args:
        file_url: Absolute path to the file on disk.
        file_type: File extension in upper case (``"PDF"``, ``"PPTX"``,
            ``"PPT"``, or ``"TXT"``).

    Returns:
        A ``(text, page_count)`` tuple where ``text`` is the concatenated
        content and ``page_count`` is the number of slides/pages.

    Raises:
        ValueError: When ``file_type`` is not one of the supported formats.
    """
    ft = file_type.upper()
    if ft == "PDF":
        return _extract_pdf(file_url)
    if ft in ("PPTX", "PPT"):
        return _extract_pptx(file_url)
    if ft == "TXT":
        return _extract_txt(file_url)
    raise ValueError(f"Unsupported file type: {file_type}")


def chunk_text(text: str, max_tokens: int = _CHUNK_TOKENS) -> list:
    """Split text into token-bounded chunks using tiktoken.

    Args:
        text: Raw input text to split.
        max_tokens: Maximum number of tokens per chunk (default 512).

    Returns:
        List of text chunk strings.  Returns an empty list when *text*
        contains only whitespace.
    """
    if not text.strip():
        return []
    enc = tiktoken.get_encoding(_ENCODING)
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i: i + max_tokens]
        chunks.append(enc.decode(chunk_tokens))
    return chunks


def _extract_pdf(path: str) -> tuple:
    """Extract text and page count from a PDF file.

    Args:
        path: Absolute path to the PDF file.

    Returns:
        A ``(text, page_count)`` tuple.
    """
    parts = []
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
    return "\n\n".join(parts), page_count


def _extract_pptx(path: str) -> tuple:
    """Extract text and slide count from a PowerPoint file.

    Args:
        path: Absolute path to the PPTX/PPT file.

    Returns:
        A ``(text, slide_count)`` tuple.
    """
    prs = Presentation(path)
    parts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                parts.append(shape.text.strip())
    return "\n\n".join(parts), len(prs.slides)


def _extract_txt(path: str) -> tuple:
    """Extract text and estimated page count from a plain-text file.

    Page count is estimated as ``max(1, line_count // 50)``.

    Args:
        path: Absolute path to the TXT file.

    Returns:
        A ``(text, page_count)`` tuple.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        text = file.read()
    page_count = max(1, len(text.split("\n")) // 50)
    return text, page_count
