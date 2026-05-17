"""Flashcard quiz mode — interactive study session from AI-generated flashcards.

This screen goes beyond a direct API mapping: it turns the raw flashcard data
returned by the AI service into a gamified self-assessment loop, tracking how
many cards the user has mastered vs. still needs to practise.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static


class QuizScreen(Screen):
    """Interactive flashcard quiz screen.

    Presents each flashcard one at a time:
      1. The question is shown first.
      2. The user presses Space (or the Reveal button) to see the answer.
      3. The user marks it as correct [Y] or wrong [N].
      4. After all cards, a score summary is shown with a retry option.

    Args:
        flashcards: List of dicts, each with ``question`` and ``answer`` keys.
        doc_title: Document title shown as the screen subtitle.
    """

    CSS = """
    QuizScreen {
        layout: vertical;
    }

    #progress-bar {
        height: 1;
        background: $panel;
        padding: 0 2;
        color: $text-muted;
        border-bottom: solid $accent;
    }

    #quiz-view {
        height: 1fr;
        layout: vertical;
        align: center middle;
        padding: 2 4;
    }

    #results-view {
        height: 1fr;
        layout: vertical;
        align: center middle;
        padding: 2 4;
    }

    #question-box {
        width: 72;
        border: round $accent;
        padding: 2 3;
        margin-bottom: 2;
        background: $surface;
    }

    .field-label {
        color: $text-muted;
        margin-bottom: 1;
        text-style: bold;
    }

    #question-text {
        text-style: bold;
        color: $text;
    }

    #answer-box {
        width: 72;
        border: round $success;
        padding: 2 3;
        margin-bottom: 1;
        background: $surface;
    }

    #answer-text {
        color: $success;
    }

    #hint-label {
        color: $text-muted;
        text-align: center;
        margin-top: 1;
    }

    #results-box {
        width: 72;
        border: double $accent;
        padding: 2 4;
        background: $surface;
    }

    #results-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }

    #results-verdict {
        text-align: center;
        margin-bottom: 1;
    }

    #results-score {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }

    #results-detail {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #results-hint {
        text-align: center;
        color: $text-muted;
    }

    #action-bar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: $panel;
        border-top: solid $accent;
    }

    #action-bar Button {
        margin-right: 1;
        height: 3;
    }

    #btn-reveal  { width: 20; }
    #btn-correct { width: 16; }
    #btn-wrong   { width: 18; }
    #btn-back    { width: 14; }
    """

    BINDINGS = [
        ("space", "reveal", "Reveal"),
        ("y", "correct", "Got it"),
        ("n", "wrong", "Wrong"),
        ("r", "retry", "Retry"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, flashcards: list[dict], doc_title: str = "") -> None:
        """Initialise quiz state.

        Args:
            flashcards: Flashcard dicts from the AI-service response.
            doc_title: Shown as part of the progress bar label.
        """
        super().__init__()
        self._cards = flashcards
        self._doc_title = doc_title
        self._index = 0
        self._correct = 0
        self._wrong = 0
        self._revealed = False
        self._finished = False

    def compose(self) -> ComposeResult:
        """Render progress bar, quiz view, results view, action bar, and footer."""
        yield Header(show_clock=True)
        yield Label("", id="progress-bar")

        # --- Quiz view ---
        with Static(id="quiz-view"):
            with Static(id="question-box"):
                yield Label("Question", classes="field-label")
                yield Label("", id="question-text")
            with Static(id="answer-box"):
                yield Label("Answer", classes="field-label")
                yield Label("", id="answer-text")
            yield Label("", id="hint-label")

        # --- Results view (hidden until quiz finishes) ---
        with Static(id="results-view"):
            with Static(id="results-box"):
                yield Label("Quiz Complete!", id="results-title")
                yield Label("", id="results-verdict")
                yield Label("", id="results-score")
                yield Label("", id="results-detail")
                yield Label("Press [R] to retry or [Esc] to go back.", id="results-hint")

        # --- Persistent action bar ---
        with Static(id="action-bar"):
            yield Button("⬛ Reveal  [Space]", id="btn-reveal", variant="primary")
            yield Button("✓ Got it  [Y]", id="btn-correct", variant="success")
            yield Button("✗ Try again [N]", id="btn-wrong", variant="error")
            yield Button("← Back [Esc]", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Hide results view and show the first card."""
        self.query_one("#results-view").display = False
        self._show_card()

    # ------------------------------------------------------------------
    # Card display helpers
    # ------------------------------------------------------------------

    def _show_card(self) -> None:
        """Render the current card (question only) and update progress."""
        if self._index >= len(self._cards):
            self._show_results()
            return

        card = self._cards[self._index]
        total = len(self._cards)

        self.query_one("#progress-bar", Label).update(
            f"  {self._doc_title}  ·  "
            f"Card {self._index + 1} / {total}  ·  "
            f"✓ {self._correct}  ✗ {self._wrong}"
        )
        self.query_one("#question-text", Label).update(card.get("question", "—"))
        self.query_one("#answer-text", Label).update(card.get("answer", "—"))
        self.query_one("#answer-box").display = False
        self.query_one("#hint-label", Label).update(
            "Press [Space] or the Reveal button to see the answer."
        )
        self._revealed = False
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        """Enable/disable action buttons based on current state."""
        self.query_one("#btn-reveal", Button).disabled = self._revealed or self._finished
        self.query_one("#btn-correct", Button).disabled = not self._revealed or self._finished
        self.query_one("#btn-wrong", Button).disabled = not self._revealed or self._finished

    def _show_results(self) -> None:
        """Switch to the results view and display the final score."""
        self._finished = True
        total = len(self._cards)
        pct = int(self._correct / total * 100) if total else 0

        if pct >= 80:
            verdict = "🎉  Excellent work!"
        elif pct >= 60:
            verdict = "👍  Good job — keep practising!"
        else:
            verdict = "📚  Keep studying — you'll get there!"

        self.query_one("#progress-bar", Label).update(
            f"  {self._doc_title}  ·  Quiz complete  ·  "
            f"Score: {self._correct}/{total} ({pct}%)"
        )
        self.query_one("#results-verdict", Label).update(verdict)
        self.query_one("#results-score", Label).update(
            f"Score: {self._correct} / {total}  ({pct}%)"
        )
        self.query_one("#results-detail", Label).update(
            f"✓ Correct: {self._correct}    ✗ Wrong: {self._wrong}"
        )
        self.query_one("#quiz-view").display = False
        self.query_one("#results-view").display = True
        self._sync_buttons()

    # ------------------------------------------------------------------
    # Bound actions
    # ------------------------------------------------------------------

    def action_reveal(self) -> None:
        """Reveal the answer for the current card."""
        if self._revealed or self._finished:
            return
        self._revealed = True
        self.query_one("#answer-box").display = True
        self.query_one("#hint-label", Label).update(
            "[Y] I knew it  ·  [N] I need more practice"
        )
        self._sync_buttons()

    def action_correct(self) -> None:
        """Mark the current card as correct and advance."""
        if not self._revealed or self._finished:
            return
        self._correct += 1
        self._index += 1
        self._show_card()

    def action_wrong(self) -> None:
        """Mark the current card as wrong and advance."""
        if not self._revealed or self._finished:
            return
        self._wrong += 1
        self._index += 1
        self._show_card()

    def action_retry(self) -> None:
        """Restart the quiz from the beginning."""
        if not self._finished:
            return
        self._index = 0
        self._correct = 0
        self._wrong = 0
        self._finished = False
        self.query_one("#results-view").display = False
        self.query_one("#quiz-view").display = True
        self._show_card()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route action-bar button clicks to the corresponding actions."""
        dispatch = {
            "btn-reveal": self.action_reveal,
            "btn-correct": self.action_correct,
            "btn-wrong": self.action_wrong,
            "btn-back": self.app.pop_screen,
        }
        if event.button.id in dispatch:
            dispatch[event.button.id]()
