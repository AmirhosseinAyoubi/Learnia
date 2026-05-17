# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Convert AI materials dict to a Markdown study guide."""


def to_markdown(data: dict) -> str:
    """Render AI-generated materials as a structured Markdown study guide.

    Produces a document with three sections: Summary, Key Concepts, and
    Flashcards.  Flashcards are formatted as bold Q/A pairs under numbered
    headings so they can be collapsed in any Markdown viewer that supports
    heading folding.

    Args:
        data: Materials dict with keys ``document_id``, ``summary``,
              ``key_concepts`` (list[str]), and ``flashcards`` (list[dict]).

    Returns:
        Rendered Markdown string (UTF-8).
    """
    doc_id = data.get("document_id", "unknown")
    summary = data.get("summary", "No summary available.")
    concepts = data.get("key_concepts", [])
    flashcards = data.get("flashcards", [])

    lines: list[str] = [
        "# Learnia Study Guide",
        "",
        f"**Document ID:** `{doc_id}`",
        "",
        "---",
        "",
        "## Summary",
        "",
        summary,
        "",
        "---",
        "",
        "## Key Concepts",
        "",
    ]

    if isinstance(concepts, list):
        for concept in concepts:
            lines.append(f"- {concept}")
    else:
        lines.append(str(concepts))

    lines += ["", "---", "", "## Flashcards", ""]

    if isinstance(flashcards, list):
        for i, card in enumerate(flashcards, 1):
            if isinstance(card, dict):
                lines += [
                    f"### Card {i}",
                    "",
                    f"**Q:** {card.get('question', '?')}",
                    "",
                    f"**A:** {card.get('answer', '?')}",
                    "",
                ]
    else:
        lines.append(str(flashcards))

    return "\n".join(lines)
