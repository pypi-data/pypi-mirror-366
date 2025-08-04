from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, TabbedContent, TabPane
from textual.containers import Horizontal, Container

from textual import events
from typing import Optional
import asyncio

from ...core.pip_api import PipAPI, Package, PackageStatus
from ..widgets.package_list import PackageList
from ..widgets.package_details import PackageDetails
from ..widgets.status_bar import StatusBar
from .install_dialog import InstallDialog
from .confirmation_dialog import ConfirmationDialog


class MainScreen(Screen):
    """Main screen with lazygit-style layout."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("i", "install", "Install"),
        ("u", "upgrade", "Upgrade"),
        ("d", "uninstall", "Uninstall"),
        ("s", "show", "Show Details"),
        ("slash", "search", "Search"),
        ("tab", "switch_focus", "Switch Panel"),
        ("ctrl+a", "upgrade_all", "Upgrade All"),
        ("f", "freeze", "Freeze"),
        ("ctrl+r", "install_requirements", "Install from requirements.txt"),
    ]

    CSS = """
    MainScreen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr;
    }

    .left-panel {
        border: solid $primary;
        margin: 1;
    }

    .right-panel {
        border: solid $secondary;
        margin: 1;
    }

    .focused {
        border: solid $accent;
    }

    #status-bar {
        dock: bottom;
        height: 3;
        background: $surface;
    }

    #header {
        dock: top;
        height: 3;
        background: $primary;
    }
    """

    def __init__(self):
        super().__init__()
        self.pip_api = PipAPI()
        self.current_focus = "left"  # "left" or "right"
        self.loading = False
        self.selected_package: Optional[Package] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the main screen."""
        yield Header(show_clock=True, id="header")

        with Horizontal():
            # Left panel - Package list with tabs
            with Container(classes="left-panel focused", id="left-panel"):
                with TabbedContent():
                    with TabPane("Installed", id="installed-tab"):
                        yield PackageList(id="installed-list")
                    with TabPane("Outdated", id="outdated-tab"):
                        yield PackageList(id="outdated-list")
                    with TabPane("Search", id="search-tab"):
                        yield PackageList(id="search-list")

            # Right panel - Package details
            with Container(classes="right-panel", id="right-panel"):
                yield PackageDetails(id="package-details")

        yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.title = "LazyPip - Python Package Manager"
        self.sub_title = "Press 'q' to quit, 'r' to refresh"
        asyncio.create_task(self.load_packages())

    async def load_packages(self) -> None:
        """Load package data asynchronously."""
        self.loading = True
        self.update_status("Loading packages...")

        try:
            # Load installed packages
            installed_packages = await asyncio.to_thread(self.pip_api.list_installed)
            installed_list = self.query_one("#installed-list", PackageList)
            installed_list.update_packages(installed_packages)

            # Load outdated packages
            outdated_packages = await asyncio.to_thread(self.pip_api.list_outdated)
            outdated_list = self.query_one("#outdated-list", PackageList)
            outdated_list.update_packages(outdated_packages)

            self.update_status(f"Loaded {len(installed_packages)} installed, {len(outdated_packages)} outdated")

        except Exception as e:
            self.update_status(f"Error loading packages: {str(e)}")
        finally:
            self.loading = False

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_refresh(self) -> None:
        """Refresh package lists."""
        if not self.loading:
            asyncio.create_task(self.load_packages())

    def action_install(self) -> None:
        """Show install dialog."""
        def install_callback(package_name: str):
            asyncio.create_task(self.install_package(package_name))

        self.app.push_screen(InstallDialog(), install_callback)

    def action_upgrade(self) -> None:
        """Upgrade selected package."""
        if self.selected_package and self.selected_package.status == PackageStatus.OUTDATED:
            asyncio.create_task(self.upgrade_package(self.selected_package.name))
        else:
            self.update_status("No upgradeable package selected")

    def action_uninstall(self) -> None:
        """Uninstall selected package."""
        if self.selected_package and self.selected_package.status == PackageStatus.INSTALLED:
            def confirm_callback(confirmed: bool):
                if confirmed and self.selected_package:
                    asyncio.create_task(self.uninstall_package(self.selected_package.name))

            self.app.push_screen(
                ConfirmationDialog(f"Uninstall {self.selected_package.name}?"),
                confirm_callback
            )
        else:
            self.update_status("No installed package selected")

    def action_show(self) -> None:
        """Show package details."""
        if self.selected_package:
            asyncio.create_task(self.load_package_details(self.selected_package.name))

    def action_search(self) -> None:
        """Focus search tab and input."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "search-tab"
        # TODO: Implement search input widget

    def action_switch_focus(self) -> None:
        """Switch focus between panels."""
        left_panel = self.query_one("#left-panel")
        right_panel = self.query_one("#right-panel")

        if self.current_focus == "left":
            left_panel.remove_class("focused")
            right_panel.add_class("focused")
            self.current_focus = "right"
        else:
            right_panel.remove_class("focused")
            left_panel.add_class("focused")
            self.current_focus = "left"

    def action_upgrade_all(self) -> None:
        """Upgrade all outdated packages."""
        def confirm_callback(confirmed: bool):
            if confirmed:
                asyncio.create_task(self.upgrade_all_packages())

        outdated_list = self.query_one("#outdated-list", PackageList)
        outdated_count = len(outdated_list.packages)

        if outdated_count > 0:
            self.app.push_screen(
                ConfirmationDialog(f"Upgrade all {outdated_count} outdated packages?"),
                confirm_callback
            )
        else:
            self.update_status("No outdated packages to upgrade")

    def action_freeze(self) -> None:
        """Show freeze output."""
        asyncio.create_task(self.show_freeze())

    def action_install_requirements(self) -> None:
        """Install from requirements.txt."""
        asyncio.create_task(self.install_from_requirements())

    async def install_package(self, package_name: str) -> None:
        """Install a package."""
        self.update_status(f"Installing {package_name}...")
        try:
            success, output = await asyncio.to_thread(
                self.pip_api.install_package, package_name
            )
            if success:
                self.update_status(f"Successfully installed {package_name}")
                await self.load_packages()  # Refresh lists
            else:
                self.update_status(f"Failed to install {package_name}")
        except Exception as e:
            self.update_status(f"Error installing {package_name}: {str(e)}")

    async def upgrade_package(self, package_name: str) -> None:
        """Upgrade a package."""
        self.update_status(f"Upgrading {package_name}...")
        try:
            success, output = await asyncio.to_thread(
                self.pip_api.upgrade_package, package_name
            )
            if success:
                self.update_status(f"Successfully upgraded {package_name}")
                await self.load_packages()  # Refresh lists
            else:
                self.update_status(f"Failed to upgrade {package_name}")
        except Exception as e:
            self.update_status(f"Error upgrading {package_name}: {str(e)}")

    async def uninstall_package(self, package_name: str) -> None:
        """Uninstall a package."""
        self.update_status(f"Uninstalling {package_name}...")
        try:
            success, output = await asyncio.to_thread(
                self.pip_api.uninstall_package, package_name
            )
            if success:
                self.update_status(f"Successfully uninstalled {package_name}")
                await self.load_packages()  # Refresh lists
            else:
                self.update_status(f"Failed to uninstall {package_name}")
        except Exception as e:
            self.update_status(f"Error uninstalling {package_name}: {str(e)}")

    async def upgrade_all_packages(self) -> None:
        """Upgrade all outdated packages."""
        self.update_status("Upgrading all outdated packages...")
        try:
            success, output = await asyncio.to_thread(self.pip_api.upgrade_all)
            if success:
                self.update_status("Successfully upgraded all packages")
            else:
                self.update_status("Some packages failed to upgrade")
            await self.load_packages()  # Refresh lists
        except Exception as e:
            self.update_status(f"Error upgrading packages: {str(e)}")

    async def load_package_details(self, package_name: str) -> None:
        """Load and display package details."""
        self.update_status(f"Loading details for {package_name}...")
        try:
            package = await asyncio.to_thread(self.pip_api.show_package, package_name)
            if package:
                details_widget = self.query_one("#package-details", PackageDetails)
                details_widget.update_package(package)
                self.update_status(f"Loaded details for {package_name}")
            else:
                self.update_status(f"Package {package_name} not found")
        except Exception as e:
            self.update_status(f"Error loading details: {str(e)}")

    async def show_freeze(self) -> None:
        """Show pip freeze output."""
        self.update_status("Generating freeze output...")
        try:
            freeze_output = await asyncio.to_thread(self.pip_api.freeze)
            # TODO: Show freeze output in a dialog or dedicated screen
            self.update_status(f"Generated freeze for {len(freeze_output)} packages")
        except Exception as e:
            self.update_status(f"Error generating freeze: {str(e)}")

    async def install_from_requirements(self) -> None:
        """Install packages from requirements.txt."""
        self.update_status("Installing from requirements.txt...")
        try:
            success, output = await asyncio.to_thread(
                self.pip_api.install_from_requirements, "requirements.txt"
            )
            if success:
                self.update_status("Successfully installed from requirements.txt")
                await self.load_packages()  # Refresh lists
            else:
                self.update_status("Failed to install from requirements.txt")
        except Exception as e:
            self.update_status(f"Error installing from requirements: {str(e)}")

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status(message)

    def on_package_list_package_selected(self, message: PackageList.PackageSelected) -> None:
        """Handle package selection from the list."""
        self.selected_package = message.package
        asyncio.create_task(self.load_package_details(message.package.name))

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if self.current_focus == "left":
            # Handle left panel navigation
            if event.key in ["j", "down"]:
                # Move down in package list
                pass
            elif event.key in ["k", "up"]:
                # Move up in package list
                pass
        elif self.current_focus == "right":
            # Handle right panel navigation
            pass
