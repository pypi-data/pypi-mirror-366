from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, Static
from textual.containers import Vertical, Horizontal


class InstallDialog(ModalScreen[str]):
    """Modal dialog for installing packages."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+c", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    InstallDialog {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: 15;
        border: thick $primary 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        color: $primary;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #package-input {
        margin: 1 0;
    }

    #buttons {
        align: center middle;
        margin-top: 1;
    }

    #install-btn {
        margin: 0 1;
    }

    #cancel-btn {
        margin: 0 1;
    }

    .hint {
        color: $text-muted;
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the install dialog layout."""
        with Vertical(id="dialog"):
            yield Label("Install Package", id="title")
            yield Static("Enter the package name to install:", classes="hint")
            yield Input(
                placeholder="Package name (e.g., requests, numpy)",
                id="package-input"
            )
            yield Static("Press Enter to install or Escape to cancel", classes="hint")
            with Horizontal(id="buttons"):
                yield Button("Install", variant="primary", id="install-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        """Focus the input when the dialog opens."""
        self.query_one("#package-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "install-btn":
            self._install_package()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field."""
        if event.input.id == "package-input":
            self._install_package()

    def _install_package(self) -> None:
        """Get the package name and dismiss with result."""
        package_input = self.query_one("#package-input", Input)
        package_name = package_input.value.strip()

        if package_name:
            self.dismiss(package_name)
        else:
            # Show error or focus input
            package_input.focus()

    def action_cancel(self) -> None:
        """Cancel the dialog."""
        self.dismiss(None)
