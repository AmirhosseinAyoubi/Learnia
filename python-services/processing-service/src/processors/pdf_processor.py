"""
processors/pdf_processor.py — Extracts plain text from PDF files.

Uses pdfplumber as the primary extractor (better layout handling)
and falls back to PyPDF2 if pdfplumber yields no text.
"""

import io
from typing import List

import pdfplumber
import PyPDF2


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.

    Args:
        file_bytes: raw bytes of the PDF file

    Returns:
        Concatenated plain text from all pages.
        Returns an empty string if no text could be extracted.
    """
    text_parts: List[str] = []

    # Primary: pdfplumber (handles tables and complex layouts better)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
    except Exception:
        pass

    if text_parts:
        return "\n\n".join(text_parts)

    # Fallback: PyPDF2
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
    except Exception:
        pass

    return "\n\n".join(text_parts)
