from textual.widgets import DataTable
from textual.widget import Widget
from textual.message import Message
from textual.app import ComposeResult
from typing import List, Optional
from rich.text import Text

from ...core.pip_api import Package, PackageStatus


class PackageList(Widget):
    """A widget displaying a list of packages with navigation and selection."""

    BINDINGS = [
        ("j", "cursor_down", "Move Down"),
        ("k", "cursor_up", "Move Up"),
        ("enter", "select", "Select Package"),
        ("space", "select", "Select Package"),
    ]

    class PackageSelected(Message):
        """Message sent when a package is selected."""

        def __init__(self, package: Package) -> None:
            super().__init__()
            self.package = package

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.packages: List[Package] = []
        self.selected_row: Optional[int] = None

    def compose(self) -> ComposeResult:
        """Create the data table."""
        table = DataTable(id="package-table")
        table.add_columns("Status", "Package", "Version", "Latest")
        table.cursor_type = "row"
        table.zebra_stripes = True
        yield table

    def update_packages(self, packages: List[Package]) -> None:
        """Update the package list."""
        self.packages = packages
        table = self.query_one("#package-table", DataTable)

        # Clear existing rows
        table.clear(columns=False)

        # Add package rows
        for package in packages:
            status_text = Text(package.status_symbol)

            # Color code status
            if package.status == PackageStatus.INSTALLED:
                status_text.stylize("green")
            elif package.status == PackageStatus.OUTDATED:
                status_text.stylize("yellow")
            elif package.status == PackageStatus.NOT_INSTALLED:
                status_text.stylize("red")
            else:
                status_text.stylize("dim")

            # Package name styling
            name_text = Text(package.name)
            if package.status == PackageStatus.OUTDATED:
                name_text.stylize("bold yellow")
            elif package.status == PackageStatus.INSTALLED:
                name_text.stylize("green")

            # Version info
            version = package.version or "unknown"
            latest = package.latest_version or "-"

            if package.status == PackageStatus.OUTDATED and package.latest_version:
                latest_text = Text(latest, style="bold yellow")
            else:
                latest_text = Text(latest)

            table.add_row(
                status_text,
                name_text,
                Text(version),
                latest_text,
                key=package.name
            )

        # Select first row if available
        if packages and table.row_count > 0:
            table.move_cursor(row=0)
            self.selected_row = 0

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        table = self.query_one("#package-table", DataTable)
        if table.row_count > 0:
            current_row = table.cursor_row
            if current_row < table.row_count - 1:
                table.move_cursor(row=current_row + 1)
                self.selected_row = current_row + 1

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        table = self.query_one("#package-table", DataTable)
        if table.row_count > 0:
            current_row = table.cursor_row
            if current_row > 0:
                table.move_cursor(row=current_row - 1)
                self.selected_row = current_row - 1

    def action_select(self) -> None:
        """Select the current package."""
        table = self.query_one("#package-table", DataTable)
        if table.row_count > 0 and self.selected_row is not None:
            if self.selected_row < len(self.packages):
                selected_package = self.packages[self.selected_row]
                self.post_message(self.PackageSelected(selected_package))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection via mouse/enter."""
        if event.row_index < len(self.packages):
            self.selected_row = event.row_index
            selected_package = self.packages[event.row_index]
            self.post_message(self.PackageSelected(selected_package))

    def get_selected_package(self) -> Optional[Package]:
        """Get the currently selected package."""
        if self.selected_row is not None and self.selected_row < len(self.packages):
            return self.packages[self.selected_row]
        return None

    def filter_packages(self, query: str) -> None:
        """Filter packages by search query."""
        if not query:
            self.update_packages(self.packages)
            return

        filtered = [
            pkg for pkg in self.packages
            if query.lower() in pkg.name.lower() or
               (pkg.summary and query.lower() in pkg.summary.lower())
        ]
        self.update_packages(filtered)

    def get_package_count(self) -> int:
        """Get the number of packages in the list."""
        return len(self.packages)

    def refresh(self) -> None:
        """Refresh the package list display."""
        self.update_packages(self.packages)
