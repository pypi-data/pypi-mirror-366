from textual.app import App
import sys

from .tui.screens.main import MainScreen
from .theme import LAZYPIP_CSS


class LazypipApp(App):
    """Main LazyPip TUI application."""

    TITLE = "LazyPip - Python Package Manager"
    SUB_TITLE = "A lazygit-style TUI for pip"

    CSS = LAZYPIP_CSS

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dark = True

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE

        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.dark = not self.dark
        self.refresh()

    def on_key(self, event) -> None:
        """Global key handler."""
        if event.key == "ctrl+c":
            self.action_quit()
        elif event.key == "ctrl+q":
            self.action_quit()


def main():
    """Entry point for the LazyPip application."""
    app = LazypipApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting LazyPip...")
        sys.exit(0)
    except Exception as e:
        print(f"Error running LazyPip: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
