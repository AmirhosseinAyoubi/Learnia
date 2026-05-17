"""Login screen — collects the API key and connects to Learnia services."""
import asyncio

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static


class LoginScreen(Screen):
    """Initial screen shown before any API key is configured.

    The user enters their Learnia X-API-Key here.  On a successful
    health-check the app transitions to the Dashboard.
    """

    CSS = """
    LoginScreen {
        align: center middle;
    }

    #login-box {
        width: 60;
        height: auto;
        border: double $accent;
        padding: 2 4;
        background: $surface;
    }

    #login-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #login-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #api-key-input {
        margin-bottom: 1;
    }

    #connect-btn {
        width: 100%;
        margin-top: 1;
    }

    #login-status {
        margin-top: 1;
        text-align: center;
        color: $warning;
        height: 1;
    }
    """

    BINDINGS = [("ctrl+q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Render the login box with API key input."""
        yield Header(show_clock=True)
        yield Static(
            """
┌─────────────────────────────────────────────┐
│        ██╗     ███████╗ █████╗ ██████╗      │
│        ██║     ██╔════╝██╔══██╗██╔══██╗     │
│        ██║     █████╗  ███████║██████╔╝     │
│        ██║     ██╔══╝  ██╔══██║██╔══██╗     │
│        ███████╗███████╗██║  ██║██║  ██║     │
│        ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝     │
│           N  I  A                            │
└─────────────────────────────────────────────┘
""",
            id="logo",
        )
        with Static(id="login-box"):
            yield Label("Learnia TUI Client", id="login-title")
            yield Label(
                "Enter your X-API-Key to connect", id="login-subtitle"
            )
            yield Input(
                placeholder="dev-api-key-1-xxxxxxxxxxxxxxxx",
                password=False,
                id="api-key-input",
            )
            yield Label("", id="login-status")
            yield Button("Connect", variant="primary", id="connect-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle the Connect button click."""
        if event.button.id == "connect-btn":
            self._try_connect()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Allow pressing Enter in the input field to connect."""
        if event.input.id == "api-key-input":
            self._try_connect()

    def _try_connect(self) -> None:
        """Read the API key and kick off the async connection attempt."""
        key = self.query_one("#api-key-input", Input).value.strip()
        if not key:
            self._set_status("Please enter your API key.", error=True)
            return
        self.query_one("#connect-btn", Button).disabled = True
        self._set_status("Connecting…")
        self._do_connect(key)

    @staticmethod
    def _status_label_text(ok: bool) -> str:
        return "✓ Connected" if ok else "✗ Failed"

    def _set_status(self, msg: str, error: bool = False) -> None:
        label = self.query_one("#login-status", Label)
        label.update(msg)
        label.add_class("error" if error else "info")

    def _do_connect(self, api_key: str) -> None:
        """Run health checks in a thread, then push DashboardScreen."""
        asyncio.get_event_loop().create_task(self._async_connect(api_key))

    async def _async_connect(self, api_key: str) -> None:
        """Validate the key by checking document-service health, then navigate."""
        from api.client import LearniaClient  # pylint: disable=import-outside-toplevel

        client = LearniaClient(api_key)
        try:
            valid = await asyncio.to_thread(client.validate_api_key)
        except Exception:  # pylint: disable=broad-except
            self._set_status("Cannot reach auth-service. Check your connection.", error=True)
            self.query_one("#connect-btn", Button).disabled = False
            return

        if not valid:
            self._set_status("Invalid or inactive API key.", error=True)
            self.query_one("#connect-btn", Button).disabled = False
            return

        self.app.api_key = api_key
        self.app.api_client = client
        self._set_status("✓ Connected!")

        from screens.dashboard import DashboardScreen  # pylint: disable=import-outside-toplevel
        await asyncio.sleep(0.4)
        self.app.push_screen(DashboardScreen())
