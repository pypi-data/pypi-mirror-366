from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Horizontal
from datetime import datetime


class StatusBar(Widget):
    """Status bar widget for displaying messages and keyboard shortcuts."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 3;
        background: $surface;
        border-top: solid $primary;
    }

    .status-content {
        padding: 0 1;
        height: 3;
    }

    .status-message {
        color: $text;
        text-align: left;
    }

    .shortcuts {
        color: $text-muted;
        text-align: right;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_message = "Ready"

    def compose(self) -> ComposeResult:
        """Create the status bar layout."""
        with Horizontal(classes="status-content"):
            yield Static(self.current_message, classes="status-message", id="status-message")
            yield Static(self._get_shortcuts_text(), classes="shortcuts", id="shortcuts")

    def update_status(self, message: str) -> None:
        """Update the status message."""
        self.current_message = message
        status_widget = self.query_one("#status-message", Static)

        # Add timestamp to message
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        status_widget.update(formatted_message)

    def _get_shortcuts_text(self) -> str:
        """Get the keyboard shortcuts text."""
        shortcuts = [
            "[bold]q[/bold]uit",
            "[bold]r[/bold]efresh",
            "[bold]i[/bold]nstall",
            "[bold]u[/bold]pgrade",
            "[bold]d[/bold]elete",
            "[bold]s[/bold]how",
            "[bold]tab[/bold] switch"
        ]
        return " | ".join(shortcuts)

    def set_loading(self, is_loading: bool) -> None:
        """Set loading state in the status bar."""
        if is_loading:
            self.update_status("Loading...")
        else:
            self.update_status("Ready")

    def show_error(self, error_message: str) -> None:
        """Show error message with red styling."""
        self.current_message = f"[red]Error: {error_message}[/red]"
        status_widget = self.query_one("#status-message", Static)
        status_widget.update(self.current_message)

    def show_success(self, success_message: str) -> None:
        """Show success message with green styling."""
        self.current_message = f"[green]✓ {success_message}[/green]"
        status_widget = self.query_one("#status-message", Static)
        status_widget.update(self.current_message)

    def show_warning(self, warning_message: str) -> None:
        """Show warning message with yellow styling."""
        self.current_message = f"[yellow]⚠ {warning_message}[/yellow]"
        status_widget = self.query_one("#status-message", Static)
        status_widget.update(self.current_message)

    def clear_message(self) -> None:
        """Clear the current message and show ready state."""
        self.update_status("Ready")
