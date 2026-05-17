# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Convert AI materials dict to a plain-text study sheet."""

_SEP = "-" * 60
_BIG_SEP = "=" * 60


def to_plain_text(data: dict) -> str:
    """Render AI-generated materials as a plain-text study sheet.

    Suitable for printing, pasting into a notes app, or reading in any
    text editor — no Markdown renderer required.

    Args:
        data: Materials dict with keys ``summary``, ``key_concepts``, and
              ``flashcards``.

    Returns:
        Plain-text string (UTF-8).
    """
    summary = data.get("summary", "No summary available.")
    concepts = data.get("key_concepts", [])
    flashcards = data.get("flashcards", [])

    lines: list[str] = [
        "LEARNIA STUDY NOTES",
        _BIG_SEP,
        "",
        "SUMMARY",
        _SEP,
        summary,
        "",
        "KEY CONCEPTS",
        _SEP,
    ]

    if isinstance(concepts, list):
        for concept in concepts:
            lines.append(f"  * {concept}")
    else:
        lines.append(str(concepts))

    lines += ["", "FLASHCARDS", _SEP, ""]

    if isinstance(flashcards, list):
        for i, card in enumerate(flashcards, 1):
            if isinstance(card, dict):
                lines += [
                    f"Q{i}: {card.get('question', '?')}",
                    f"A{i}: {card.get('answer', '?')}",
                    "",
                ]
    else:
        lines.append(str(flashcards))

    return "\n".join(lines)
