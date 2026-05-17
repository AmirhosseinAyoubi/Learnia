"""API Keys screen — list, create, and revoke Learnia API keys."""
import asyncio
import platform
import subprocess

from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

# ---------------------------------------------------------------------------
# New-key modal
# ---------------------------------------------------------------------------

class NewKeyModal(ModalScreen):
    """Modal for entering a user ID and note when creating a new API key."""

    CSS = """
    NewKeyModal {
        align: center middle;
    }

    #new-key-box {
        width: 60;
        height: auto;
        border: double $accent;
        padding: 2 4;
        background: $surface;
    }

    #new-key-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
        text-align: center;
    }

    #new-key-box Label {
        margin-bottom: 0;
    }

    #new-key-box Input {
        margin-bottom: 1;
    }

    #new-key-buttons {
        layout: horizontal;
        margin-top: 1;
        height: auto;
    }

    #new-key-buttons Button {
        width: 1fr;
        margin: 0 1;
    }

    #new-key-error {
        color: $error;
        margin-top: 1;
        height: 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        """Render the create-key form."""
        with Static(id="new-key-box"):
            yield Label("Create New API Key", id="new-key-title")
            yield Label("User ID (UUID)")
            yield Input(
                placeholder="11111111-1111-1111-1111-111111111111",
                id="user-id-input",
            )
            yield Label("Note / description")
            yield Input(placeholder="e.g. dev key for testing", id="note-input")
            yield Label("", id="new-key-error")
            with Static(id="new-key-buttons"):
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Submit or cancel the create-key form."""
        if event.button.id == "btn-create":
            self._submit()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Dismiss without creating a key."""
        self.dismiss(None)

    def _submit(self) -> None:
        """Validate inputs and dismiss with the form data."""
        user_id = self.query_one("#user-id-input", Input).value.strip()
        note = self.query_one("#note-input", Input).value.strip()
        err = self.query_one("#new-key-error", Label)

        if not user_id:
            err.update("User ID is required.")
            return
        if not note:
            err.update("Note is required.")
            return

        self.dismiss({"user_id": user_id, "note": note})


# ---------------------------------------------------------------------------
# Revoke confirmation modal
# ---------------------------------------------------------------------------

class RevokeModal(ModalScreen):
    """Confirmation dialog before revoking an API key."""

    CSS = """
    RevokeModal {
        align: center middle;
    }

    #revoke-box {
        width: 50;
        height: auto;
        border: double $error;
        padding: 2 4;
        background: $surface;
    }

    #revoke-msg {
        margin-bottom: 2;
        text-align: center;
    }

    #revoke-buttons {
        layout: horizontal;
        height: auto;
    }

    #revoke-buttons Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, note: str) -> None:
        """Store the key note for display."""
        super().__init__()
        self._note = note

    def compose(self) -> ComposeResult:
        """Render the revoke confirmation prompt."""
        with Static(id="revoke-box"):
            yield Label(
                f'Revoke key "{self._note}"?\nThe key will stop working immediately.',
                id="revoke-msg",
            )
            with Static(id="revoke-buttons"):
                yield Button("Revoke", variant="error", id="btn-confirm")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Confirm or cancel the revocation."""
        self.dismiss(event.button.id == "btn-confirm")

    def action_cancel(self) -> None:
        """Dismiss without revoking."""
        self.dismiss(False)


# ---------------------------------------------------------------------------
# Result modal (shows newly created key value once)
# ---------------------------------------------------------------------------

class KeyCreatedModal(ModalScreen):
    """Displays the newly created key value — shown once, cannot be retrieved again."""

    CSS = """
    KeyCreatedModal {
        align: center middle;
    }

    #key-created-box {
        width: 64;
        height: auto;
        border: double $success;
        padding: 2 4;
        background: $surface;
    }

    #key-created-title {
        text-style: bold;
        color: $success;
        text-align: center;
        margin-bottom: 1;
    }

    #key-value-label {
        background: $panel;
        padding: 1 2;
        margin: 1 0;
        text-align: center;
    }

    #key-warning {
        color: $warning;
        text-align: center;
        margin-bottom: 2;
    }

    #key-ok-btn {
        width: 100%;
        margin-bottom: 1;
    }

    #key-copy-btn {
        width: 100%;
    }

    #key-copy-status {
        color: $success;
        text-align: center;
        height: 1;
        margin-top: 1;
    }
    """

    def __init__(self, key_value: str) -> None:
        """Store the new key value for display.

        Args:
            key_value: The plaintext API key returned by the server (shown once).
        """
        super().__init__()
        self._key_value = key_value

    def compose(self) -> ComposeResult:
        """Render the key display with copy-to-clipboard and dismiss buttons."""
        with Static(id="key-created-box"):
            yield Label("API Key Created!", id="key-created-title")
            yield Label("Copy this key now — it will not be shown again:", id="key-warning")
            yield Label(self._key_value, id="key-value-label")
            yield Label("", id="key-copy-status")
            yield Button("📋 Copy to Clipboard", variant="default", id="key-copy-btn")
            yield Button("I've copied it", variant="primary", id="key-ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle copy and dismiss button clicks."""
        if event.button.id == "key-copy-btn":
            self._copy_to_clipboard()
        else:
            self.dismiss()

    def _copy_to_clipboard(self) -> None:
        """Copy the key value to the system clipboard using platform commands.

        Falls back gracefully if clipboard access is unavailable.
        """
        status = self.query_one("#key-copy-status", Label)
        try:
            sys_name = platform.system()
            if sys_name == "Darwin":
                subprocess.run(["pbcopy"], input=self._key_value.encode(), check=True)
            elif sys_name == "Linux":
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=self._key_value.encode(),
                    check=True,
                )
            elif sys_name == "Windows":
                subprocess.run(
                    ["clip"], input=self._key_value.encode("utf-16"), check=True
                )
            else:
                status.update("Clipboard not supported on this platform.")
                return
            status.update("✓ Copied to clipboard!")
        except FileNotFoundError:
            status.update("Clipboard tool not found — please copy manually.")
        except subprocess.CalledProcessError:
            status.update("Copy failed — please copy manually.")


# ---------------------------------------------------------------------------
# API Keys screen
# ---------------------------------------------------------------------------

class APIKeysScreen(Screen):
    """Displays all API keys for a user and allows creating or revoking them.

    Keybindings:
        n — open NewKeyModal to create a key
        r — open RevokeModal to revoke the selected key
        Escape — return to Dashboard
    """

    CSS = """
    APIKeysScreen {
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

    #keys-table {
        height: 1fr;
    }

    #keys-status {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("n", "new_key", "New Key"),
        ("r", "revoke_key", "Revoke"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        """Initialise with an empty key cache."""
        super().__init__()
        self._keys: list[dict] = []
        self._user_id: str = ""

    def compose(self) -> ComposeResult:
        """Render toolbar, key table, and status bar."""
        yield Header(show_clock=True)
        with Static(id="toolbar"):
            yield Button("➕ New Key [N]", id="btn-new", variant="primary")
            yield Button("🚫 Revoke  [R]", id="btn-revoke", variant="error")
        yield DataTable(id="keys-table", cursor_type="row", zebra_stripes=True)
        yield Label("Enter a User ID to load keys…", id="keys-status")
        yield Footer()

    def on_mount(self) -> None:
        """Add table columns; prompt user for a User ID to load keys."""
        table = self.query_one(DataTable)
        table.add_columns("Note", "Active", "Created", "ID (short)")
        self._prompt_user_id()

    def _prompt_user_id(self) -> None:
        """Ask for a user ID via a modal then load that user's keys."""
        from textual.screen import ModalScreen as _MS  # pylint: disable=import-outside-toplevel

        class UserIdModal(_MS):
            """Inline modal for entering a User ID to look up keys."""

            CSS = """
            UserIdModal { align: center middle; }
            #uid-box {
                width: 60; height: auto;
                border: double $accent; padding: 2 4; background: $surface;
            }
            #uid-title { text-style: bold; color: $accent; margin-bottom: 1; text-align: center; }
            #uid-hint { color: $text-muted; margin-bottom: 1; }
            #uid-input { margin-bottom: 1; }
            #uid-btn { width: 100%; }
            """

            BINDINGS = [("escape", "cancel", "Cancel")]

            def compose(self) -> ComposeResult:
                with Static(id="uid-box"):
                    yield Label("API Keys", id="uid-title")
                    yield Label(
                        "Enter your User ID (UUID) to manage keys:",
                        id="uid-hint",
                    )
                    yield Input(
                        placeholder="11111111-1111-1111-1111-111111111111",
                        id="uid-input",
                    )
                    yield Button("Load Keys", variant="primary", id="uid-btn")

            def on_button_pressed(self, event: Button.Pressed) -> None:
                val = self.query_one("#uid-input", Input).value.strip()
                self.dismiss(val or None)

            def on_input_submitted(self, _: Input.Submitted) -> None:
                val = self.query_one("#uid-input", Input).value.strip()
                self.dismiss(val or None)

            def action_cancel(self) -> None:
                self.dismiss(None)

        def _handle(user_id: str | None) -> None:
            if user_id:
                self._user_id = user_id
                asyncio.get_event_loop().create_task(self._load_keys())
            else:
                self.app.pop_screen()

        self.app.push_screen(UserIdModal(), _handle)

    async def _load_keys(self) -> None:
        """Fetch all API keys for the stored user ID and populate the table."""
        self._set_status("Loading keys…")
        try:
            self._keys = await asyncio.to_thread(
                self.app.api_client.list_api_keys, self._user_id
            )
        except Exception as exc:  # pylint: disable=broad-except
            self._set_status(f"Error: {exc}")
            return

        table = self.query_one(DataTable)
        table.clear()
        for key in self._keys:
            short_id = str(key.get("id", ""))[:8] + "…"
            active = "✓ yes" if key.get("active") else "✗ no"
            created = str(key.get("createdAt", ""))[:10]
            table.add_row(
                key.get("note", "—"),
                active,
                created,
                short_id,
            )
        self._set_status(f"{len(self._keys)} key(s) for user {self._user_id[:8]}…")

    def _set_status(self, msg: str) -> None:
        self.query_one("#keys-status", Label).update(msg)

    def _selected_key(self) -> dict | None:
        table = self.query_one(DataTable)
        if not self._keys or table.cursor_row is None:
            return None
        idx = table.cursor_row
        return self._keys[idx] if 0 <= idx < len(self._keys) else None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route toolbar button clicks."""
        if event.button.id == "btn-new":
            self.action_new_key()
        elif event.button.id == "btn-revoke":
            self.action_revoke_key()

    def action_new_key(self) -> None:
        """Open the new-key modal and create the key on submission."""
        def _handle(result: dict | None) -> None:
            if result:
                asyncio.get_event_loop().create_task(
                    self._do_create_key(result["user_id"], result["note"])
                )

        self.app.push_screen(NewKeyModal(), _handle)

    async def _do_create_key(self, user_id: str, note: str) -> None:
        """Create the key and show the result modal."""
        self._set_status("Creating key…")
        try:
            key_data = await asyncio.to_thread(
                self.app.api_client.create_api_key, user_id, note
            )
            key_value = key_data.get("keyValue", "(key value not returned)")
            self.app.push_screen(KeyCreatedModal(key_value))
            self._user_id = user_id
            await self._load_keys()
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Create failed: {exc}", severity="error")
            self._set_status(f"Error: {exc}")

    def action_revoke_key(self) -> None:
        """Open the revoke confirmation for the selected key."""
        key = self._selected_key()
        if not key:
            self.notify("No key selected.", severity="warning")
            return

        def _handle(confirmed: bool) -> None:
            if confirmed:
                asyncio.get_event_loop().create_task(self._do_revoke(key))

        self.app.push_screen(RevokeModal(key.get("note", "?")), _handle)

    async def _do_revoke(self, key: dict) -> None:
        """Revoke the key and refresh the list."""
        self._set_status("Revoking key…")
        try:
            await asyncio.to_thread(
                self.app.api_client.revoke_api_key, key["id"]
            )
            self.notify("Key revoked.")
            await self._load_keys()
        except Exception as exc:  # pylint: disable=broad-except
            self.notify(f"Revoke failed: {exc}", severity="error")
