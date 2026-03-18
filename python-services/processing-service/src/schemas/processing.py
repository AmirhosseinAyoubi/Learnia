"""
schemas/processing.py — Pydantic models for the processing service API.
"""

from pydantic import BaseModel
from typing import List


class TextChunk(BaseModel):
    """
    A single chunk of extracted text.

    Attributes:
        index:      zero-based position of this chunk in the document
        text:       the extracted text content
        char_count: number of characters in this chunk
    """
    index: int
    text: str
    char_count: int


class ProcessingResponse(BaseModel):
    """
    Response returned by POST /api/v1/processing/process.

    Attributes:
        filename:    original uploaded filename
        file_type:   detected file type (PDF, PPTX, TXT)
        chunk_count: total number of chunks produced
        chunks:      list of TextChunk objects
        _links:      HATEOAS navigation links
    """
    filename: str
    file_type: str
    chunk_count: int
    chunks: List[TextChunk]
    links: dict = {}

    class Config:
        # serialize links as _links in JSON responses
        populate_by_name = True

    def model_post_init(self, __context):
        # rename 'links' → '_links' is handled in the router via response_model
        pass
