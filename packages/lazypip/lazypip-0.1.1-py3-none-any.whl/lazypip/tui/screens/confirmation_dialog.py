from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical, Horizontal


class ConfirmationDialog(ModalScreen[bool]):
    """Modal dialog for confirming destructive operations."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+c", "cancel", "Cancel"),
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    DEFAULT_CSS = """
    ConfirmationDialog {
        align: center middle;
    }

    #dialog {
        width: 50;
        height: 12;
        border: thick $warning 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        color: $warning;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #message {
        text-align: center;
        margin: 1 0;
        color: $text;
    }

    #buttons {
        align: center middle;
        margin-top: 2;
    }

    #yes-btn {
        margin: 0 1;
    }

    #no-btn {
        margin: 0 1;
    }

    .hint {
        color: $text-muted;
        text-align: center;
        margin: 1 0;
    }
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.confirmation_message = message

    def compose(self) -> ComposeResult:
        """Create the confirmation dialog layout."""
        with Vertical(id="dialog"):
            yield Label("Confirmation", id="title")
            yield Label(self.confirmation_message, id="message")
            yield Label("Are you sure you want to proceed?", classes="hint")
            yield Label("Press Y to confirm, N or Escape to cancel", classes="hint")
            with Horizontal(id="buttons"):
                yield Button("Yes", variant="error", id="yes-btn")
                yield Button("No", variant="default", id="no-btn")

    def on_mount(self) -> None:
        """Focus the No button by default for safety."""
        self.query_one("#no-btn", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "yes-btn":
            self.dismiss(True)
        elif event.button.id == "no-btn":
            self.dismiss(False)

    def action_confirm(self) -> None:
        """Confirm the action (Y key)."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel the action (N key or Escape)."""
        self.dismiss(False)
