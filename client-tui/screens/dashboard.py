"""Dashboard screen — navigation hub with service health and document count."""
import asyncio

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static


class DashboardScreen(Screen):
    """Central navigation hub shown after login.

    Displays a summary panel (service health + document count) and
    navigation buttons leading to the Documents and API Keys screens.
    """

    CSS = """
    DashboardScreen {
        layout: vertical;
    }

    #content {
        layout: horizontal;
        height: 1fr;
    }

    #sidebar {
        width: 22;
        background: $panel;
        border-right: solid $accent;
        padding: 2 1;
    }

    #sidebar-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 2;
    }

    #sidebar Button {
        width: 100%;
        margin-bottom: 1;
    }

    #main {
        padding: 2 4;
        height: 1fr;
    }

    #welcome {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .health-row {
        margin-bottom: 1;
    }

    .health-ok {
        color: $success;
    }

    .health-fail {
        color: $error;
    }

    #stats-box {
        border: round $accent;
        padding: 1 2;
        margin-top: 1;
        width: 40;
        height: auto;
    }

    #stats-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("1", "goto_documents", "Documents"),
        ("2", "goto_keys", "API Keys"),
        ("escape", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Render the sidebar navigation and main stats panel."""
        yield Header(show_clock=True)
        with Static(id="content"):
            with Static(id="sidebar"):
                yield Label("LEARNIA", id="sidebar-title")
                yield Button("📄 Documents [1]", id="btn-docs", variant="primary")
                yield Button("🔑 API Keys  [2]", id="btn-keys")
                yield Button("🚪 Quit", id="btn-quit", variant="error")
            with Static(id="main"):
                yield Label("Dashboard", id="welcome")
                yield Label("Checking services…", id="health-doc", classes="health-row")
                yield Label("", id="health-ai", classes="health-row")
                yield Label("", id="health-auth", classes="health-row")
                with Static(id="stats-box"):
                    yield Label("Statistics", id="stats-title")
                    yield Label("Documents: loading…", id="stat-docs")
        yield Footer()

    def on_mount(self) -> None:
        """Load health and stats on screen entry."""
        asyncio.get_event_loop().create_task(self._load())

    async def _load(self) -> None:
        """Check health of all three services and fetch the document count."""
        client = self.app.api_client

        for svc, label_id in (
            ("document", "health-doc"),
            ("ai", "health-ai"),
            ("auth", "health-auth"),
        ):
            ok = await asyncio.to_thread(client.health, svc)
            label = self.query_one(f"#{label_id}", Label)
            icon = "✓" if ok else "✗"
            label.update(f"{icon}  {svc}-service")
            label.add_class("health-ok" if ok else "health-fail")

        try:
            docs = await asyncio.to_thread(client.list_documents)
            count = len(docs)
        except Exception:  # pylint: disable=broad-except
            count = "?"

        self.query_one("#stat-docs", Label).update(f"Documents: {count}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Route sidebar button clicks to the appropriate screen."""
        if event.button.id == "btn-docs":
            self.action_goto_documents()
        elif event.button.id == "btn-keys":
            self.action_goto_keys()
        elif event.button.id == "btn-quit":
            self.app.exit()

    def action_goto_documents(self) -> None:
        """Navigate to the Documents list screen."""
        from screens.documents import DocumentsScreen  # pylint: disable=import-outside-toplevel
        self.app.push_screen(DocumentsScreen())

    def action_goto_keys(self) -> None:
        """Navigate to the API Keys management screen."""
        from screens.api_keys import APIKeysScreen  # pylint: disable=import-outside-toplevel
        self.app.push_screen(APIKeysScreen())
