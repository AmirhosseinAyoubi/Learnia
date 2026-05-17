# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Convert AI materials dict to Anki-compatible tab-separated values.

Anki import format reference:
  https://docs.ankiweb.net/importing/text-files.html
"""


def _sanitise(text: str) -> str:
    """Strip characters that break Anki's TSV parser.

    Args:
        text: Raw field value.

    Returns:
        Value with tabs and newlines replaced by spaces.
    """
    return str(text).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def to_anki_csv(data: dict) -> str:
    """Render flashcards as an Anki-importable tab-separated file.

    The header comments tell Anki how to interpret the file:
    - ``#separator:tab`` — field delimiter
    - ``#html:false`` — treat content as plain text
    - ``#columns:Front\\tBack`` — column mapping to Basic note type fields
    - ``#notetype:Basic`` — target note type

    Import in Anki via: **File → Import**, then select this file.  Make sure
    the note type is set to *Basic* and the separator to *Tab*.

    Args:
        data: Materials dict with a ``flashcards`` key (list[dict]).

    Returns:
        Anki TSV string (UTF-8).
    """
    flashcards = data.get("flashcards", [])

    lines: list[str] = [
        "#separator:tab",
        "#html:false",
        "#columns:Front\tBack",
        "#notetype:Basic",
        "#deck:Learnia",
    ]

    if isinstance(flashcards, list):
        for card in flashcards:
            if isinstance(card, dict):
                front = _sanitise(card.get("question", ""))
                back = _sanitise(card.get("answer", ""))
                if front and back:
                    lines.append(f"{front}\t{back}")

    return "\n".join(lines)
