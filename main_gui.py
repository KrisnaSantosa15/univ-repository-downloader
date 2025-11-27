"""
UPI Repository Downloader - GUI Version
Entry point for the Flet-based graphical user interface
"""
import flet as ft
from src.gui.main_window import MainWindow


def main(page: ft.Page):
    """Main entry point for Flet application"""
    # Page configuration
    page.title = "UPI Repository Downloader"
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Set theme colors
    page.theme = ft.Theme(
        color_scheme_seed="blue",
        use_material3=True,
    )

    # Create and show main window
    main_window = MainWindow(page)
    page.add(main_window)
    page.update()


if __name__ == "__main__":
    # Run the Flet app
    ft.app(target=main)
