"""Document detail screen — shows document info and AI study materials in tabs."""
import asyncio
import os

from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

# ---------------------------------------------------------------------------
# Export modal
# ---------------------------------------------------------------------------


class ExportModal(ModalScreen):
    """Modal for choosing export format and output file path."""

    CSS = """
    ExportModal {
        align: center middle;
    }

    #export-box {
        width: 64;
        height: auto;
        border: double $accent;
        padding: 2 4;
        background: $surface;
    }

    #export-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 2;
    }

    #export-box Label {
        margin-bottom: 0;
    }

    #export-box Select, #export-box Input {
        margin-bottom: 1;
    }

    #export-error {
        color: $error;
        height: 1;
        margin-top: 1;
    }

    #export-buttons {
        layout: horizontal;
        margin-top: 1;
        height: auto;
    }

    #export-buttons Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    _FORMAT_OPTIONS = [
        ("Markdown study guide (.md)", "markdown"),
        ("Anki flashcard import (.txt)", "anki"),
        ("Plain text notes (.txt)", "text"),
    ]

    def compose(self) -> ComposeResult:
        """Render the export format selector and save-path input."""
        with Static(id="export-box"):
            yield Label("Export Study Materials", id="export-title")
            yield Label("Format")
            yield Select(self._FORMAT_OPTIONS, value="markdown", id="fmt-select")
            yield Label("Save to file path")
            yield Input(placeholder="~/Desktop/study-guide.md", id="path-input")
            yield Label("", id="export-error")
            with Static(id="export-buttons"):
                yield Button("Export", variant="primary", id="btn-export")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Submit or cancel the export form."""
        if event.button.id == "btn-export":
            self._submit()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Dismiss without exporting."""
        self.dismiss(None)

    def _submit(self) -> None:
        """Validate inputs and dismiss with the export parameters."""
        fmt = self.query_one("#fmt-select", Select).value
        path = self.query_one("#path-input", Input).value.strip()
        err = self.query_one("#export-error", Label)

        if not path:
            err.update("File path is required.")
            return

        expanded = os.path.expanduser(path)
        parent = os.path.dirname(expanded) or "."
        if not os.path.isdir(parent):
            err.update(f"Directory does not exist: {parent}")
            return

        self.dismiss({"format": fmt, "path": expanded})


class DocumentDetailScreen(Screen):
    """Displays full document metadata and its AI-generated study materials.

    Three material tabs are shown: Summary, Key Concepts, and Flashcards.
    If no materials have been generated yet, an Analyze button triggers the
    OpenAI pipeline.  A Delete Materials button removes all stored materials.
    A Quiz button launches an interactive flashcard session (QuizScreen).

    Args:
        doc: Document dict from the document-service list endpoint.
    """

    CSS = """
    DocumentDetailScreen {
        layout: vertical;
    }

    #info-bar {
        height: auto;
        background: $panel;
        padding: 1 2;
        border-bottom: solid $accent;
        layout: horizontal;
    }

    #info-bar Static {
        width: 1fr;
    }

    .info-label {
        color: $text-muted;
    }

    .info-value {
        color: $text;
        text-style: bold;
    }

    #action-bar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: $panel;
        border-bottom: solid $accent;
    }

    #action-bar Button {
        margin-right: 1;
        height: 3;
    }

    #tabs-area {
        height: 1fr;
    }

    .material-content {
        padding: 1 2;
        height: 1fr;
        overflow-y: auto;
    }

    #status-detail {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("a", "analyze", "Analyze"),
        ("q", "quiz", "Quiz"),
        ("e", "export", "Export"),
        ("x", "delete_materials", "Delete Materials"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, doc: dict) -> None:
        """Store the document dict for display.

        Args:
            doc: Document metadata dict from the list-documents endpoint.
        """
        super().__init__()
        self._doc = doc
        self._materials: dict = {}  # cached after first successful load

    def compose(self) -> ComposeResult:
        """Render the info bar, action bar, and tabbed material area."""
        doc = self._doc
        yield Header(show_clock=True)

        # Info bar
        with Static(id="info-bar"):
            with Static():
                yield Label("Title", classes="info-label")
                yield Label(doc.get("title", "—"), classes="info-value")
            with Static():
                yield Label("Type", classes="info-label")
                yield Label(doc.get("fileType", "—"), classes="info-value")
            with Static():
                yield Label("Status", classes="info-label")
                yield Label(doc.get("status", "—"), id="status-value", classes="info-value")
            with Static():
                yield Label("ID", classes="info-label")
                yield Label(str(doc.get("id", "—"))[:8] + "…", classes="info-value")

        # Action bar
        with Static(id="action-bar"):
            yield Button("🤖 Analyze [A]", id="btn-analyze", variant="primary")
            yield Button("🃏 Quiz [Q]", id="btn-quiz", variant="success")
            yield Button("📤 Export [E]", id="btn-export", variant="default")
            yield Button("🗑 Delete Materials [X]", id="btn-delete-mat", variant="error")
            yield Button("← Back [Esc]", id="btn-back")

        # Tabbed material area
        with TabbedContent(id="tabs-area"):
            with TabPane("📝 Summary", id="tab-summary"):
                yield Static("Loading…", id="content-summary", classes="material-content")
            with TabPane("🔑 Key Concepts", id="tab-concepts"):
                yield Static("Loading…", id="content-concepts", classes="material-content")
            with TabPane("🃏 Flashcards", id="tab-flashcards"):
                yield Static("Loading…", id="content-flashcards", classes="material-content")

        yield Label("Fetching AI materials…", id="status-detail")
        yield Footer()

    def on_mount(self) -> None:
        """Load AI materials when the screen is first displayed."""
        asyncio.get_event_loop().create_task(self._load_materials())

    async def _load_materials(self) -> None:
        """Fetch materials from the AI service and populate the three tabs."""
        self._set_status("Fetching AI materials…")
        try:
            data = await asyncio.to_thread(
                self.app.api_client.get_ai_materials, self._doc["id"]
            )
            self._materials = data
            self._populate(data)
            self._set_status("Materials loaded.")
        except Exception as exc:  # pylint: disable=broad-except
            code = getattr(exc, "status_code", 0)
            if code == 404:
                msg = "No AI materials yet — press [A] to analyze."
                for widget_id in ("content-summary", "content-concepts", "content-flashcards"):
                    self.query_one(f"#{widget_id}", Static).update(msg)
                self._set_status("No materials found.")
            else:
                status = f" (HTTP {code})" if code else ""
                self._set_status(f"Error{status}: {exc}")

    def _populate(self, data: dict) -> None:
        """Fill in Summary, Key Concepts, and Flashcards from the API response.

        Args:
            data: Materials dict with ``summary``, ``key_concepts``, ``flashcards``.
        """
        # Summary tab
        summary = data.get("summary", "No summary available.")
        self.query_one("#content-summary", Static).update(summary)

        # Key Concepts tab
        concepts = data.get("key_concepts", [])
        if isinstance(concepts, list):
            concept_text = "\n".join(f"  • {c}" for c in concepts) or "—"
        else:
            concept_text = str(concepts)
        self.query_one("#content-concepts", Static).update(concept_text)

        # Flashcards tab
        flashcards = data.get("flashcards", [])
        if isinstance(flashcards, list):
            lines = []
            for i, card in enumerate(flashcards, 1):
                if isinstance(card, dict):
                    lines.append(f"Q{i}: {card.get('question', '?')}")
                    lines.append(f"A{i}: {card.get('answer', '?')}")
                    lines.append("")
                else:
                    lines.append(str(card))
            card_text = "\n".join(lines).strip() or "—"
        else:
            card_text = str(flashcards)
        self.query_one("#content-flashcards", Static).update(card_text)

    def _set_status(self, msg: str) -> None:
        """Update the bottom status bar."""
        self.query_one("#status-detail", Label).update(msg)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route action bar button clicks."""
        dispatch = {
            "btn-analyze": self.action_analyze,
            "btn-quiz": self.action_quiz,
            "btn-export": self.action_export,
            "btn-delete-mat": self.action_delete_materials,
            "btn-back": self.app.pop_screen,
        }
        if event.button.id in dispatch:
            dispatch[event.button.id]()

    def action_analyze(self) -> None:
        """Call the AI analyze endpoint for this document."""
        asyncio.get_event_loop().create_task(self._do_analyze())

    async def _do_analyze(self) -> None:
        """Run AI analysis and reload materials on success."""
        self._set_status("Calling OpenAI… (this may take up to 30 seconds)")
        for widget_id in ("content-summary", "content-concepts", "content-flashcards"):
            self.query_one(f"#{widget_id}", Static).update("Analyzing…")
        try:
            await asyncio.to_thread(
                self.app.api_client.analyze_document, self._doc["id"]
            )
            self.notify("Analysis complete!")
            await self._load_materials()
        except Exception as exc:  # pylint: disable=broad-except
            code = getattr(exc, "status_code", 0)
            status = f" (HTTP {code})" if code else ""
            self.notify(f"Analysis failed{status}: {exc}", severity="error")
            self._set_status(f"Analysis failed{status}: {exc}")

    def action_quiz(self) -> None:
        """Launch flashcard quiz mode if materials are available."""
        flashcards = self._materials.get("flashcards", [])
        if not flashcards:
            self.notify(
                "No flashcards available. Run [A] Analyze first.",
                severity="warning",
            )
            return
        from screens.quiz import QuizScreen  # pylint: disable=import-outside-toplevel

        self.app.push_screen(
            QuizScreen(flashcards, doc_title=self._doc.get("title", ""))
        )

    def action_export(self) -> None:
        """Open the export modal to save study materials to a file."""
        if not self._materials:
            self.notify("No materials to export. Run [A] Analyze first.", severity="warning")
            return
        self.app.push_screen(ExportModal(), self._handle_export_result)

    def _handle_export_result(self, result: dict | None) -> None:
        """Receive the dismissed result from ExportModal and kick off the download."""
        if result:
            asyncio.get_event_loop().create_task(self._do_export(result["format"], result["path"]))

    async def _do_export(self, fmt: str, path: str) -> None:
        """Call the export service then write the bytes to disk."""
        self._set_status(f"Exporting as {fmt}…")
        try:
            data = await asyncio.to_thread(
                self.app.api_client.export_materials, self._doc["id"], fmt
            )
            with open(path, "wb") as fh:
                fh.write(data)
            self.notify(f"Exported to {path}")
            self._set_status(f"Exported to {path}")
        except Exception as exc:  # pylint: disable=broad-except
            code = getattr(exc, "status_code", 0)
            status = f" (HTTP {code})" if code else ""
            self.notify(f"Export failed{status}: {exc}", severity="error")
            self._set_status(f"Export failed{status}: {exc}")

    def action_delete_materials(self) -> None:
        """Delete all AI materials for this document."""
        asyncio.get_event_loop().create_task(self._do_delete_materials())

    async def _do_delete_materials(self) -> None:
        """Call delete-materials API then refresh the tabs."""
        self._set_status("Deleting materials…")
        try:
            await asyncio.to_thread(
                self.app.api_client.delete_ai_materials, self._doc["id"]
            )
            self._materials = {}
            self.notify("AI materials deleted.")
            await self._load_materials()
        except Exception as exc:  # pylint: disable=broad-except
            code = getattr(exc, "status_code", 0)
            status = f" (HTTP {code})" if code else ""
            self.notify(f"Delete failed{status}: {exc}", severity="error")
