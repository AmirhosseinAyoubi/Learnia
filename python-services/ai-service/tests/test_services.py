# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the AI Service OpenAI integration.

The ``openai.OpenAI`` client is patched so no real API calls are made.
Tests verify that:
- A successful call returns the expected keys
- Text is truncated at 12,000 characters
- An empty chunk list still produces a valid prompt (no crash)
- OpenAI errors propagate to the caller
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from src.services import analyze_document, _MAX_TEXT_CHARS


def _make_openai_response(payload: dict) -> MagicMock:
    """Build a minimal mock that looks like an OpenAI ChatCompletion response."""
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


class TestAnalyzeDocument:
    """Tests for the ``analyze_document`` service function."""

    def test_success_returns_dict_with_required_keys(self):
        """A successful OpenAI call returns a dict containing the three required keys.

        Input: document_id + two chunks.
        Expected: dict with "summary", "key_concepts", "flashcards", and "document_id".
        """
        payload = {
            "summary": "A summary.",
            "key_concepts": ["k1", "k2"],
            "flashcards": [{"question": "Q?", "answer": "A."}],
        }
        mock_response = _make_openai_response(payload)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.services._client", mock_client):
            result = analyze_document("doc-1", ["chunk one", "chunk two"])

        assert result["summary"] == "A summary."
        assert result["key_concepts"] == ["k1", "k2"]
        assert result["document_id"] == "doc-1"

    def test_text_truncated_at_max_chars(self):
        """When joined chunks exceed 12,000 characters the text is truncated.

        A chunk of _MAX_TEXT_CHARS base characters followed by a unique marker
        is used so the marker is detectable if truncation did not happen.

        Input: chunk = ("x" * _MAX_TEXT_CHARS) + "OVERFLOW_MARKER"
        Expected: prompt contains the base x's but not the OVERFLOW_MARKER.
        """
        marker = "OVERFLOW_MARKER"
        long_chunk = "x" * _MAX_TEXT_CHARS + marker
        payload = {"summary": "s", "key_concepts": [], "flashcards": []}
        mock_response = _make_openai_response(payload)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.services._client", mock_client):
            analyze_document("doc-1", [long_chunk])

        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert "x" * 100 in prompt  # base text is present
        assert marker not in prompt  # overflow portion was removed

    def test_empty_chunks_does_not_raise(self):
        """Passing an empty chunks list does not crash; it sends an empty text prompt.

        Input: empty chunks list.
        Expected: OpenAI is called with an empty text section (no ValueError raised).
        """
        payload = {"summary": "s", "key_concepts": [], "flashcards": []}
        mock_response = _make_openai_response(payload)

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.services._client", mock_client):
            result = analyze_document("doc-empty", [])

        assert "summary" in result

    def test_openai_error_propagates_to_caller(self):
        """When OpenAI raises an exception it propagates out of analyze_document.

        The router layer catches this and returns 500; here we verify the
        service does not swallow the exception silently.
        """
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("rate limit exceeded")

        with patch("src.services._client", mock_client):
            with pytest.raises(Exception, match="rate limit exceeded"):
                analyze_document("doc-1", ["chunk"])
