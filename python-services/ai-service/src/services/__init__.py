# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""OpenAI integration for generating structured study materials.

Uses ``gpt-4o-mini`` with ``response_format={"type": "json_object"}`` so the
model always returns valid JSON.  The module lazily initialises the OpenAI
client the first time it is called so that missing API keys only raise at
call-time, not at import time.
"""
import json
import logging

from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None

_MAX_TEXT_CHARS = 12_000

_PROMPT_TEMPLATE = """You are an expert educational content creator. \
Given the following document text, generate structured study materials in JSON format.

Document text:
{text}

Generate a JSON object with exactly these fields:
- "summary": A concise 2-3 paragraph summary of the main content
- "key_concepts": A list of 5-10 key concepts or terms from the document, each as a string
- "flashcards": A list of 5-10 flashcard objects, each with "question" and "answer" string fields

Return ONLY valid JSON, no other text."""


def _get_client() -> OpenAI:
    """Return (and lazily initialise) the global OpenAI client.

    Returns:
        Configured :class:`openai.OpenAI` instance.
    """
    global _client  # pylint: disable=global-statement
    if _client is None:
        kwargs: dict = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        _client = OpenAI(**kwargs)
    return _client


def analyze_document(document_id: str, chunks: list) -> dict:
    """Call OpenAI to generate study materials from a list of text chunks.

    Joins all chunks into a single string (truncated to ``_MAX_TEXT_CHARS``
    characters to stay within model context limits) and sends a single
    completion request asking for a JSON object with ``summary``,
    ``key_concepts``, and ``flashcards``.

    Args:
        document_id: UUID string of the document being analysed (added to
            the returned dict for convenience).
        chunks: Ordered list of text chunk strings extracted from the document.

    Returns:
        Dict with keys ``document_id``, ``summary``, ``key_concepts``,
        and ``flashcards``.

    Raises:
        openai.OpenAIError: On any API-level error (auth, rate limit, etc.).
        json.JSONDecodeError: If the model returns malformed JSON despite the
            ``json_object`` response format instruction.
    """
    text = "\n\n".join(chunks)
    if len(text) > _MAX_TEXT_CHARS:
        text = text[:_MAX_TEXT_CHARS]

    prompt = _PROMPT_TEMPLATE.format(text=text)

    logger.info(
        "Calling OpenAI for document_id=%s, text_length=%d",
        document_id, len(text),
    )

    response = _get_client().chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.openai_max_tokens,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    result["document_id"] = document_id
    logger.info("OpenAI response received for document_id=%s", document_id)
    return result
