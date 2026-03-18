"""
services/processing_service.py — Orchestrates document processing.

Responsibilities:
1. Detect file type from the filename extension.
2. Dispatch to the appropriate processor (PDF / PPTX / TXT).
3. Split the extracted text into fixed-size chunks suitable for
   downstream embedding and retrieval.
"""

from typing import List, Tuple

from ..processors import (
    extract_text_from_pdf,
    extract_text_from_pptx,
    extract_text_from_txt,
)
from ..schemas import TextChunk

# Maximum characters per chunk (~400–500 words).
# Kept deliberately small so each chunk fits in an LLM context window.
CHUNK_SIZE = 1500
# Overlap between consecutive chunks so context is not lost at boundaries.
CHUNK_OVERLAP = 150

SUPPORTED_TYPES = {"pdf", "pptx", "ppt", "txt", "text"}


def detect_file_type(filename: str) -> str:
    """
    Derive the file type from the filename extension.

    Args:
        filename: original filename including extension

    Returns:
        Uppercase file type string, e.g. "PDF", "PPTX", "TXT".

    Raises:
        ValueError: if the extension is not supported.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        return "PDF"
    if ext in ("pptx", "ppt"):
        return "PPTX"
    if ext in ("txt", "text"):
        return "TXT"
    raise ValueError(
        f"Unsupported file type '.{ext}'. Supported: PDF, PPTX, TXT."
    )


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """
    Extract raw text from a document.

    Args:
        file_bytes: raw file content
        file_type:  one of "PDF", "PPTX", "TXT"

    Returns:
        Plain text string extracted from the document.

    Raises:
        ValueError: if file_type is unrecognised.
        RuntimeError: if extraction fails.
    """
    try:
        if file_type == "PDF":
            return extract_text_from_pdf(file_bytes)
        if file_type == "PPTX":
            return extract_text_from_pptx(file_bytes)
        if file_type == "TXT":
            return extract_text_from_txt(file_bytes)
    except Exception as exc:
        raise RuntimeError(f"Text extraction failed: {exc}") from exc

    raise ValueError(f"Unknown file type: {file_type}")


def chunk_text(text: str) -> List[TextChunk]:
    """
    Split text into overlapping fixed-size chunks.

    The algorithm walks through the text in steps of
    (CHUNK_SIZE - CHUNK_OVERLAP), producing chunks of at most CHUNK_SIZE
    characters. Chunks are paragraph-aware: splits prefer whitespace
    boundaries when possible.

    Args:
        text: plain text to chunk

    Returns:
        Ordered list of TextChunk objects.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[TextChunk] = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    start = 0
    index = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        # Try to end the chunk at a paragraph or sentence boundary
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1:
                boundary = text.rfind(". ", start, end)
            if boundary != -1:
                end = boundary + 1  # include the delimiter

        chunk_text_content = text[start:end].strip()
        if chunk_text_content:
            chunks.append(
                TextChunk(
                    index=index,
                    text=chunk_text_content,
                    char_count=len(chunk_text_content),
                )
            )
            index += 1

        start += step

    return chunks


def process_document(file_bytes: bytes, filename: str) -> Tuple[str, List[TextChunk]]:
    """
    Full pipeline: detect type → extract text → chunk.

    Args:
        file_bytes: raw uploaded file content
        filename:   original filename (used to detect type)

    Returns:
        A tuple of (file_type, list_of_chunks).

    Raises:
        ValueError: for unsupported file types or empty documents.
        RuntimeError: if text extraction fails.
    """
    file_type = detect_file_type(filename)
    text = extract_text(file_bytes, file_type)

    if not text.strip():
        raise ValueError("No text could be extracted from the document.")

    chunks = chunk_text(text)
    return file_type, chunks
