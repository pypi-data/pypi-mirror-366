from textual.widgets import Footer, Static
from textual.app import ComposeResult


class LazypipFooter(Footer):
    """Enhanced footer with comprehensive keyboard shortcuts."""

    DEFAULT_CSS = """
    LazypipFooter {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }

    .footer-content {
        padding: 0 1;
        color: $text;
    }

    .shortcut {
        color: $accent;
        text-style: bold;
    }

    .separator {
        color: $text-muted;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Create the footer layout with shortcuts."""
        shortcuts_text = self._create_shortcuts_text()
        yield Static(shortcuts_text, classes="footer-content")

    def _create_shortcuts_text(self) -> str:
        """Create the keyboard shortcuts display text."""
        shortcuts = [
            ("[bold]q[/bold]uit", "Quit application"),
            ("[bold]r[/bold]efresh", "Refresh package lists"),
            ("[bold]i[/bold]nstall", "Install new package"),
            ("[bold]u[/bold]pgrade", "Upgrade selected package"),
            ("[bold]d[/bold]elete", "Uninstall package"),
            ("[bold]s[/bold]how", "Show package details"),
            ("[bold]tab[/bold]", "Switch panels"),
            ("[bold]/[/bold]", "Search packages"),
            ("[bold]ctrl+a[/bold]", "Upgrade all"),
            ("[bold]f[/bold]reeze", "Show requirements"),
        ]

        # Format shortcuts for display
        formatted_shortcuts = []
        for key, desc in shortcuts:
            formatted_shortcuts.append(f"{key}")

        return " [dim]|[/dim] ".join(formatted_shortcuts)

    def update_context(self, context: str):
        """Update footer based on current context."""
        context_shortcuts = {
            "package_list": [
                ("[bold]↑↓[/bold]/[bold]jk[/bold]", "Navigate"),
                ("[bold]enter[/bold]", "Select"),
                ("[bold]i[/bold]nstall", "Install"),
                ("[bold]u[/bold]pgrade", "Upgrade"),
                ("[bold]d[/bold]elete", "Uninstall"),
            ],
            "package_details": [
                ("[bold]tab[/bold]", "Back to list"),
                ("[bold]i[/bold]nstall", "Install"),
                ("[bold]u[/bold]pgrade", "Upgrade"),
                ("[bold]d[/bold]elete", "Uninstall"),
            ],
            "search": [
                ("[bold]enter[/bold]", "Search"),
                ("[bold]esc[/bold]", "Cancel"),
                ("[bold]↑↓[/bold]", "Navigate results"),
            ]
        }

        if context in context_shortcuts:
            shortcuts = context_shortcuts[context]
            formatted = []
            for key, desc in shortcuts:
                formatted.append(f"{key}")

            shortcuts_text = " [dim]|[/dim] ".join(formatted)
            footer_widget = self.query_one(Static)
            footer_widget.update(shortcuts_text)


class StatusFooter(Static):
    """Alternative footer that shows both status and shortcuts."""

    DEFAULT_CSS = """
    StatusFooter {
        dock: bottom;
        height: 2;
        background: $surface;
        border-top: solid $primary;
        padding: 0 1;
    }

    .status-line {
        color: $text;
        height: 1;
    }

    .shortcuts-line {
        color: $text-muted;
        height: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_message = "Ready"

    def compose(self) -> ComposeResult:
        """Create the two-line footer."""
        yield Static(self.status_message, classes="status-line", id="status-line")
        yield Static(self._get_shortcuts(), classes="shortcuts-line", id="shortcuts-line")

    def update_status(self, message: str):
        """Update the status message."""
        self.status_message = message
        status_widget = self.query_one("#status-line")
        status_widget.update(message)

    def _get_shortcuts(self) -> str:
        """Get shortcuts text."""
        return "[bold]q[/bold]uit [bold]r[/bold]efresh [bold]i[/bold]nstall [bold]u[/bold]pgrade [bold]d[/bold]elete [bold]s[/bold]how [bold]tab[/bold] switch [bold]/[/bold] search"
