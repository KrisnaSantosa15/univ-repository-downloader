"""
Main Window Component
Manages navigation and page routing for the GUI application
"""
import flet as ft
from src.gui.pages.welcome_page import WelcomePage
from src.gui.pages.download_page import DownloadPage
from src.gui.pages.convert_page import ConvertPage
from src.gui.pages.settings_page import SettingsPage
from src.gui.pages.info_page import InfoPage
from src.gui.pages.files_page import FilesPage
from src.config.config import Config
import os


class MainWindow(ft.Container):
    """Main window with sidebar navigation"""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.config = self._load_or_create_config()

        # Current page reference
        self.current_page = None

        # Initialize UI
        self._build_ui()

        # Show welcome page if first run, otherwise show download page
        if self._is_first_run():
            self._navigate_to("welcome")
        else:
            self._navigate_to("download")

    def _load_or_create_config(self):
        """Load config from file or create default"""
        config_file = "download_config.txt"

        if os.path.exists(config_file):
            # Load from file
            config_data = {}
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config_data[key] = value

            return Config(
                cookie_string=config_data.get('cookie_string', 'empty'),
                document_id=config_data.get('document_id', '130155'),
                document_title=config_data.get('document_title', 'My Thesis')
            )
        else:
            # Create default config
            return Config()

    def _is_first_run(self):
        """Check if this is the first run (no config file exists)"""
        return not os.path.exists("download_config.txt")

    def _build_ui(self):
        """Build the main UI structure"""
        # Sidebar navigation
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    selected_icon=ft.Icons.DOWNLOAD,
                    label="Download",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    selected_icon=ft.Icons.FOLDER,
                    label="Files",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.TRANSFORM_OUTLINED,
                    selected_icon=ft.Icons.TRANSFORM,
                    label="Convert",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INFO_OUTLINED,
                    selected_icon=ft.Icons.INFO,
                    label="Info",
                ),
            ],
            on_change=self._on_nav_change,
            bgcolor="surfacevariant",
        )

        # Content area
        self.content_area = ft.Container(
            content=ft.Text("Loading..."),
            expand=True,
            padding=20,
        )

        # Main layout
        self.content = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
        self.expand = True

    def _on_nav_change(self, e):
        """Handle navigation rail selection change"""
        routes = ["welcome", "download", "files",
                  "convert", "settings", "info"]
        selected_route = routes[e.control.selected_index]
        self._navigate_to(selected_route)

    def _navigate_to(self, route: str):
        """Navigate to a specific page"""
        # Update nav rail selection
        route_indices = {
            "welcome": 0,
            "download": 1,
            "files": 2,
            "convert": 3,
            "settings": 4,
            "info": 5,
        }
        if route in route_indices:
            self.nav_rail.selected_index = route_indices[route]

        # Create new page instance
        if route == "welcome":
            self.current_page = WelcomePage(self)
        elif route == "download":
            self.current_page = DownloadPage(self)
        elif route == "files":
            self.current_page = FilesPage(self)
        elif route == "convert":
            self.current_page = ConvertPage(self)
        elif route == "settings":
            self.current_page = SettingsPage(self)
        elif route == "info":
            self.current_page = InfoPage(self)

        # Update content area
        self.content_area.content = self.current_page
        self.page.update()

        # Call did_mount lifecycle hook if available
        if hasattr(self.current_page, 'did_mount'):
            self.current_page.did_mount()

    def save_config(self):
        """Save configuration to file"""
        config_file = "download_config.txt"
        with open(config_file, 'w') as f:
            f.write(f"cookie_string={self.config.cookie_string}\n")
            f.write(f"document_id={self.config.document_id}\n")
            f.write(f"document_title={self.config.document_title}\n")
            f.write(f"ocr_language={self.config.ocr_language}\n")

    def reload_config(self):
        """Reload configuration from file"""
        self.config = self._load_or_create_config()
