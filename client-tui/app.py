"""Learnia TUI — entry point."""

from textual.app import App


class LearniaApp(App):
    """Root application class.  Holds shared state (api_key, api_client)
    so every screen can reach them via ``self.app``."""

    TITLE = "Learnia TUI"
    SUB_TITLE = "AI-powered study tool"

    BINDINGS = [("ctrl+q", "quit", "Quit")]

    # Shared state set by LoginScreen after a successful connection
    api_key: str = ""
    api_client = None  # type: LearniaClient | None  # noqa: F821

    def on_mount(self) -> None:
        """Push the login screen as the first screen."""
        from screens.login import LoginScreen  # pylint: disable=import-outside-toplevel
        self.push_screen(LoginScreen())


if __name__ == "__main__":  # pragma: no cover
    app = LearniaApp()
    app.run()
