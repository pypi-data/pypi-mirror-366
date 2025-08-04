from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Vertical
from typing import Optional

from ...core.pip_api import Package, PackageStatus


class PackageDetails(Widget):
    """Widget for displaying detailed package information."""

    DEFAULT_CSS = """
    PackageDetails {
        border: solid $primary;
        padding: 1;
    }

    .package-header {
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }

    .package-info {
        padding: 1;
    }

    .no-selection {
        text-align: center;
        color: $text-muted;
        padding: 3;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_package: Optional[Package] = None

    def compose(self) -> ComposeResult:
        """Create the package details layout."""
        with Vertical():
            yield Static("No package selected", classes="no-selection", id="details-content")

    def update_package(self, package: Optional[Package]) -> None:
        """Update the displayed package information."""
        self.current_package = package
        content_widget = self.query_one("#details-content", Static)

        if not package:
            content_widget.update("No package selected")
            content_widget.add_class("no-selection")
            return

        content_widget.remove_class("no-selection")

        # Create rich content for the package
        details_text = self._create_package_details(package)
        content_widget.update(details_text)

    def _create_package_details(self, package: Package) -> str:
        """Create formatted package details."""
        lines = []

        # Header with package name and status
        status_symbol = package.status_symbol
        status_color = self._get_status_color(package.status)

        lines.append(f"[bold blue]{package.name}[/bold blue] {status_symbol}")
        lines.append("")

        # Version information
        if package.version:
            lines.append(f"[bold]Version:[/bold] {package.version}")

        if package.latest_version and package.status == PackageStatus.OUTDATED:
            lines.append(f"[bold]Latest:[/bold] [yellow]{package.latest_version}[/yellow]")

        if package.version and package.latest_version and package.status == PackageStatus.OUTDATED:
            lines.append(f"[bold red]⚠ Update available![/bold red]")

        lines.append("")

        # Summary
        if package.summary:
            lines.append(f"[bold]Summary:[/bold]")
            lines.append(f"  {package.summary}")
            lines.append("")

        # Location
        if package.location:
            lines.append(f"[bold]Location:[/bold]")
            lines.append(f"  {package.location}")
            lines.append("")

        # Dependencies
        if package.requires:
            lines.append(f"[bold]Requires:[/bold]")
            for req in package.requires:
                lines.append(f"  • {req}")
            lines.append("")

        if package.required_by:
            lines.append(f"[bold]Required by:[/bold]")
            for req in package.required_by:
                lines.append(f"  • {req}")
            lines.append("")

        # Status-specific information
        if package.status == PackageStatus.INSTALLED:
            lines.append("[green]✓ Package is installed[/green]")
        elif package.status == PackageStatus.OUTDATED:
            lines.append("[yellow]↑ Package can be upgraded[/yellow]")
            lines.append(f"[dim]Run: pip install --upgrade {package.name}[/dim]")
        elif package.status == PackageStatus.NOT_INSTALLED:
            lines.append("[red]✗ Package is not installed[/red]")
            lines.append(f"[dim]Run: pip install {package.name}[/dim]")

        lines.append("")

        # Action hints
        lines.append("[dim]Actions:[/dim]")
        if package.status == PackageStatus.INSTALLED:
            lines.append("[dim]  [u] Upgrade (if outdated)[/dim]")
            lines.append("[dim]  [d] Uninstall[/dim]")
        elif package.status == PackageStatus.OUTDATED:
            lines.append("[dim]  [u] Upgrade to latest[/dim]")
            lines.append("[dim]  [d] Uninstall current[/dim]")
        elif package.status == PackageStatus.NOT_INSTALLED:
            lines.append("[dim]  [i] Install package[/dim]")

        lines.append("[dim]  [s] Show details[/dim]")

        return "\n".join(lines)

    def _get_status_color(self, status: PackageStatus) -> str:
        """Get color for package status."""
        colors = {
            PackageStatus.INSTALLED: "green",
            PackageStatus.OUTDATED: "yellow",
            PackageStatus.NOT_INSTALLED: "red",
            PackageStatus.UNKNOWN: "dim"
        }
        return colors.get(status, "dim")

    def clear(self) -> None:
        """Clear the package details."""
        self.update_package(None)

    def get_current_package(self) -> Optional[Package]:
        """Get the currently displayed package."""
        return self.current_package
