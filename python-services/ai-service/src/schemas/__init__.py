# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Pydantic request/response models for the AI Service."""
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Request body for the ``POST /api/v1/ai/analyze`` endpoint.

    Attributes:
        document_id: UUID string of the document whose stored chunks
            should be retrieved and analysed.
    """

    document_id: str


class Flashcard(BaseModel):
    """A single flashcard with a question and its answer.

    Attributes:
        question: The question side of the flashcard.
        answer: The answer side of the flashcard.
    """

    question: str
    answer: str


class AnalyzeResponse(BaseModel):
    """Response body returned after a successful analysis.

    Attributes:
        document_id: UUID string of the analysed document.
        summary: 2-3 paragraph plain-text summary.
        key_concepts: List of 5-10 important terms or concepts.
        flashcards: List of 5-10 question/answer flashcard pairs.
    """

    document_id: str
    summary: str
    key_concepts: list
    flashcards: list
