"""Documents screen — lists all documents and exposes upload / delete / detail actions."""
import asyncio
import os

from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

# ---------------------------------------------------------------------------
# Upload modal
# ---------------------------------------------------------------------------

class UploadModal(ModalScreen):
    """Inline modal for entering document title and local file path before upload."""

    CSS = """
    UploadModal {
        align: center middle;
    }

    #upload-box {
        width: 64;
        height: auto;
        border: double $accent;
        padding: 2 4;
        background: $surface;
    }

    #upload-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
        text-align: center;
    }

    #upload-box Label {
        margin-bottom: 0;
    }

    #upload-box Input {
        margin-bottom: 1;
    }

    #upload-buttons {
        layout: horizontal;
        margin-top: 1;
        height: auto;
    }

    #upload-buttons Button {
        width: 1fr;
        margin: 0 1;
    }

    #upload-error {
        color: $error;
        margin-top: 1;
        height: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        """Render the upload form."""
        with Static(id="upload-box"):
            yield Label("Upload Document", id="upload-title")
            yield Label("Title")
            yield Input(placeholder="e.g. Machine Learning Lecture 3", id="doc-title")
            yield Label("Local file path")
            yield Input(placeholder="/home/user/docs/lecture3.pdf", id="file-path")
            yield Label("", id="upload-error")
            with Static(id="upload-buttons"):
                yield Button("Upload", variant="primary", id="btn-submit")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Submit or cancel the upload form."""
        if event.button.id == "btn-submit":
            self._submit()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Dismiss without uploading."""
        self.dismiss(None)

    def _submit(self) -> None:
        """Validate inputs and dismiss with the form data."""
        title = self.query_one("#doc-title", Input).value.strip()
        path = self.query_one("#file-path", Input).value.strip()
        err_label = self.query_one("#upload-error", Label)

        if not title:
            err_label.update("Title is required.")
            return
        if not path:
            err_label.update("File path is required.")
            return
        if not os.path.exists(path):
            err_label.update(f"File not found: {path}")
            return

        self.dismiss({"title": title, "path": path})


# ---------------------------------------------------------------------------
# Delete confirmation modal
# ---------------------------------------------------------------------------

class DeleteModal(ModalScreen):
    """Confirmation dialog before permanently deleting a document."""

    CSS = """
    DeleteModal {
        align: center middle;
    }

    #delete-box {
        width: 50;
        height: auto;
        border: double $error;
        padding: 2 4;
        background: $surface;
    }

    #delete-msg {
        margin-bottom: 2;
        text-align: center;
    }

    #delete-buttons {
        layout: horizontal;
        height: auto;
    }

    #delete-buttons Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, doc_title: str) -> None:
        """Store the document title for display in the confirmation message."""
        super().__init__()
        self._doc_title = doc_title

    def compose(self) -> ComposeResult:
        """Render the confirmation prompt."""
        with Static(id="delete-box"):
            yield Label(
                f'Delete "{self._doc_title}"?\nThis cannot be undone.',
                id="delete-msg",
            )
            with Static(id="delete-buttons"):
                yield Button("Delete", variant="error", id="btn-confirm")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Confirm or cancel the deletion."""
        self.dismiss(event.button.id == "btn-confirm")

    def action_cancel(self) -> None:
        """Dismiss without deleting."""
        self.dismiss(False)


# ---------------------------------------------------------------------------
# Documents screen
# ---------------------------------------------------------------------------

class DocumentsScreen(Screen):
    """Displays a table of all uploaded documents.

    Keybindings:
        u   — open UploadModal to upload a new document
        d   — open DeleteModal to delete the selected document
        a   — trigger AI analysis for the selected document
        Enter — open DocumentDetailScreen for the selected document
        Escape — return to Dashboard
    """

    CSS = """
    DocumentsScreen {
        layout: vertical;
    }

    #toolbar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: $panel;
        border-bottom: solid $accent;
    }

    #toolbar Button {
        margin-right: 1;
        height: 3;
    }

    #doc-table {
        height: 1fr;
    }

    #status-bar {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("u", "upload", "Upload"),
        ("d", "delete_doc", "Delete"),
        ("a", "analyze", "Analyze"),
        ("r", "refresh", "Refresh"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        """Initialise the screen with an empty document cache."""
        super().__init__()
        self._docs: list[dict] = []

    def compose(self) -> ComposeResult:
        """Render the toolbar, document table, and status bar."""
        yield Header(show_clock=True)
        with Static(id="toolbar"):
            yield Button("⬆ Upload [U]", id="btn-upload", variant="primary")
            yield Button("🗑 Delete [D]", id="btn-delete", variant="error")
            yield Button("🤖 Analyze [A]", id="btn-analyze")
            yield Button("↺ Refresh [R]", id="btn-refresh")
        yield DataTable(id="doc-table", cursor_type="row", zebra_stripes=True)
        yield Label("Loading documents…", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Add table columns and load documents on first display."""
        table = self.query_one(DataTable)
        table.add_columns("Title", "Type", "Status", "Created")
        asyncio.get_event_loop().create_task(self._load_docs())

    async def _load_docs(self) -> None:
        """Fetch documents from the API and populate the DataTable."""
        self._set_status("Loading…")
        try:
            self._docs = await asyncio.to_thread(self.app.api_client.list_documents)
        except Exception as exc:  # pylint: disable=broad-except
            self._set_status(f"Error: {exc}")
            return

        table = self.query_one(DataTable)
        table.clear()
        for doc in self._docs:
            created = (doc.get("createdAt") or "")[:10]
            table.add_row(
                doc.get("title", "—"),
                doc.get("fileType", "—"),
                doc.get("status", "—"),
                created,
            )
        self._set_status(f"{len(self._docs)} document(s)")

    def _set_status(self, msg: str) -> None:
        """Update the bottom status bar text."""
        self.query_one("#status-bar", Label).update(msg)

    def _selected_doc(self) -> dict | None:
        """Return the document dict for the currently highlighted table row."""
        table = self.query_one(DataTable)
        if not self._docs or table.cursor_row is None:
            return None
        idx = table.cursor_row
        return self._docs[idx] if 0 <= idx < len(self._docs) else None

    # ---- button events ----

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route toolbar button clicks to the corresponding actions."""
        mapping = {
            "btn-upload": self.action_upload,
            "btn-delete": self.action_delete_doc,
            "btn-analyze": self.action_analyze,
            "btn-refresh": self.action_refresh,
        }
        if event.button.id in mapping:
            mapping[event.button.id]()

    # ---- keybinding actions ----

    def action_upload(self) -> None:
        """Open the upload modal and process the result."""
        def _handle(result: dict | None) -> None:
            if result:
                asyncio.get_event_loop().create_task(
                    self._do_upload(result["title"], result["path"])
                )

        self.app.push_screen(UploadModal(), _handle)

    async def _do_upload(self, title: str, path: str) -> None:
        """Execute the two-step upload: store file then create metadata record."""
        self._set_status("Uploading file…")
        try:
            upload_resp = await asyncio.to_thread(
                self.app.api_client.upload_file, path, title
            )
            file_name = upload_resp.get("fileName", os.path.basename(path))
            file_url = upload_resp.get("fileUrl", f"/uploads/{file_name}")
            file_size = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lstrip(".").upper() or "UNKNOWN"

            self._set_status("Saving document record…")
            await asyncio.to_thread(
                self.app.api_client.create_document,
                title,
                file_name,
                ext,
                file_size,
                file_url,
            )
            self.notify("Document uploaded and queued for processing.")
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Upload failed: {exc}", severity="error")
        finally:
            await self._load_docs()

    def action_delete_doc(self) -> None:
        """Open delete confirmation for the selected document."""
        doc = self._selected_doc()
        if not doc:
            self.notify("No document selected.", severity="warning")
            return

        def _handle(confirmed: bool) -> None:
            if confirmed:
                asyncio.get_event_loop().create_task(self._do_delete(doc))

        self.app.push_screen(DeleteModal(doc.get("title", "?")), _handle)

    async def _do_delete(self, doc: dict) -> None:
        """Call the delete API then refresh the list."""
        self._set_status("Deleting…")
        try:
            await asyncio.to_thread(
                self.app.api_client.delete_document, doc["id"]
            )
            self.notify("Document deleted.")
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Delete failed: {exc}", severity="error")
        finally:
            await self._load_docs()

    def action_analyze(self) -> None:
        """Trigger AI analysis for the selected document."""
        doc = self._selected_doc()
        if not doc:
            self.notify("No document selected.", severity="warning")
            return
        asyncio.get_event_loop().create_task(self._do_analyze(doc))

    async def _do_analyze(self, doc: dict) -> None:
        """Call the AI analyze endpoint and notify on completion."""
        self._set_status(f"Analyzing '{doc.get('title', '?')}' with AI…")
        try:
            await asyncio.to_thread(
                self.app.api_client.analyze_document, doc["id"]
            )
            self.notify("AI analysis complete. Open document detail to view.")
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Analysis failed: {exc}", severity="error")
        finally:
            self._set_status(f"{len(self._docs)} document(s)")

    def action_refresh(self) -> None:
        """Reload the document list from the server."""
        asyncio.get_event_loop().create_task(self._load_docs())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Open DocumentDetailScreen when the user presses Enter on a row."""
        doc = self._selected_doc()
        if doc:
            from screens.document_detail import (
                DocumentDetailScreen,  # pylint: disable=import-outside-toplevel
            )
            self.app.push_screen(DocumentDetailScreen(doc))
