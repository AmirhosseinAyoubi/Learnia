# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the three export formatters."""

from src.formatters.anki_csv import to_anki_csv
from src.formatters.markdown import to_markdown
from src.formatters.plain_text import to_plain_text

SAMPLE = {
    "document_id": "aaaa-bbbb",
    "summary": "This is a test summary.",
    "key_concepts": ["Concept A", "Concept B"],
    "flashcards": [
        {"question": "What is A?", "answer": "A is alpha."},
        {"question": "What is B?", "answer": "B is beta."},
    ],
}


class TestMarkdownFormatter:
    """Tests for the Markdown study-guide formatter."""

    def test_contains_summary(self):
        """Summary text appears in the output."""
        result = to_markdown(SAMPLE)
        assert "This is a test summary." in result

    def test_contains_key_concepts(self):
        """Key concepts are rendered as list items."""
        result = to_markdown(SAMPLE)
        assert "- Concept A" in result
        assert "- Concept B" in result

    def test_contains_flashcard_questions(self):
        """Flashcard questions appear with bold Q: prefix."""
        result = to_markdown(SAMPLE)
        assert "**Q:** What is A?" in result
        assert "**Q:** What is B?" in result

    def test_contains_flashcard_answers(self):
        """Flashcard answers appear with bold A: prefix."""
        result = to_markdown(SAMPLE)
        assert "**A:** A is alpha." in result

    def test_has_document_id(self):
        """Document ID appears as a code-span."""
        result = to_markdown(SAMPLE)
        assert "`aaaa-bbbb`" in result

    def test_empty_flashcards(self):
        """Handles missing flashcards without error."""
        result = to_markdown({"document_id": "x", "summary": "s", "key_concepts": []})
        assert "## Flashcards" in result

    def test_non_list_concepts(self):
        """Handles key_concepts as a plain string without error."""
        result = to_markdown({**SAMPLE, "key_concepts": "raw string"})
        assert "raw string" in result


class TestAnkiCsvFormatter:
    """Tests for the Anki TSV formatter."""

    def test_header_lines_present(self):
        """All required Anki header comment lines are included."""
        result = to_anki_csv(SAMPLE)
        assert "#separator:tab" in result
        assert "#html:false" in result
        assert "#notetype:Basic" in result

    def test_flashcard_rows(self):
        """Each flashcard produces a tab-separated question/answer row."""
        result = to_anki_csv(SAMPLE)
        assert "What is A?\tA is alpha." in result
        assert "What is B?\tB is beta." in result

    def test_tabs_stripped_from_content(self):
        """Tabs inside field values are replaced with spaces."""
        data = {
            "flashcards": [{"question": "Q\twith\ttabs", "answer": "A\there"}]
        }
        result = to_anki_csv(data)
        assert "\t\t" not in result  # no double-tab within a field

    def test_newlines_stripped_from_content(self):
        """Newlines inside field values are replaced with spaces."""
        data = {
            "flashcards": [{"question": "Q\nline2", "answer": "A\nline2"}]
        }
        result = to_anki_csv(data)
        lines = result.splitlines()
        data_lines = [ln for ln in lines if not ln.startswith("#")]
        assert len(data_lines) == 1

    def test_empty_flashcards(self):
        """Returns only header lines when there are no flashcards."""
        result = to_anki_csv({"flashcards": []})
        lines = [ln for ln in result.splitlines() if not ln.startswith("#")]
        assert lines == []

    def test_skips_non_dict_cards(self):
        """Non-dict entries in the flashcard list are silently ignored."""
        data = {"flashcards": ["not a dict", {"question": "Q", "answer": "A"}]}
        result = to_anki_csv(data)
        data_lines = [ln for ln in result.splitlines() if not ln.startswith("#")]
        assert len(data_lines) == 1


class TestPlainTextFormatter:
    """Tests for the plain-text study sheet formatter."""

    def test_contains_summary(self):
        """Summary section appears in output."""
        result = to_plain_text(SAMPLE)
        assert "This is a test summary." in result

    def test_contains_key_concepts(self):
        """Key concepts are bullet-formatted."""
        result = to_plain_text(SAMPLE)
        assert "  * Concept A" in result

    def test_contains_flashcards(self):
        """Flashcards rendered with Q/A prefix and index."""
        result = to_plain_text(SAMPLE)
        assert "Q1: What is A?" in result
        assert "A1: A is alpha." in result

    def test_section_headers_present(self):
        """All three section headers are present."""
        result = to_plain_text(SAMPLE)
        assert "SUMMARY" in result
        assert "KEY CONCEPTS" in result
        assert "FLASHCARDS" in result

    def test_empty_data(self):
        """Handles completely empty data dict without error."""
        result = to_plain_text({})
        assert "LEARNIA STUDY NOTES" in result
