"""
Files Page for GUI
File explorer with PDF viewer
"""
import os
import flet as ft
from pathlib import Path


class FilesPage(ft.Container):
    """Files page with file explorer and PDF viewer"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.page = main_window.page
        self.config = main_window.config

        # State - start at parent to show all document folders
        output_path = Path(self.config.output_dir)
        # Go up to 'downloaded' folder
        self.downloads_root = str(output_path.parent)
        self.current_path = self.downloads_root
        self.breadcrumb_items = []
        self.selected_pdf = None

        # Build UI
        self._build_ui()
        self.expand = True
        self.padding = 20

    def did_mount(self):
        """Called after the page is added to the view"""
        self._refresh_file_list()

    def _build_ui(self):
        """Build the files page UI"""
        # Title
        title = ft.Text(
            "📁 Files",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # Breadcrumb navigation
        self.breadcrumb = ft.Row([], spacing=5, wrap=True)

        # File list
        self.file_list = ft.ListView(
            spacing=5,
            padding=10,
            expand=True,
        )

        # PDF viewer
        self.pdf_viewer = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=100, color="grey"),
                ft.Text("Select a PDF file to view", size=16, color="grey"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            bgcolor="grey50",
            border_radius=10,
            padding=20,
            expand=True,
        )

        # Layout with split view
        file_panel = ft.Container(
            content=ft.Column([
                ft.Text("File Explorer", weight=ft.FontWeight.BOLD, size=18),
                self.breadcrumb,
                ft.Divider(),
                self.file_list,
            ], spacing=10, expand=True),
            width=400,
            padding=10,
            border=ft.border.all(1, "grey300"),
            border_radius=10,
        )

        pdf_panel = ft.Container(
            content=ft.Column([
                ft.Text("PDF Viewer", weight=ft.FontWeight.BOLD, size=18),
                ft.Divider(),
                self.pdf_viewer,
            ], spacing=10, expand=True),
            padding=10,
            border=ft.border.all(1, "grey300"),
            border_radius=10,
            expand=True,
        )

        # Layout
        self.content = ft.Column([
            title,
            ft.Container(
                content=ft.Row([
                    file_panel,
                    pdf_panel,
                ], spacing=15, expand=True),
                expand=True,
            ),
        ], spacing=15, expand=True)

    def _refresh_file_list(self):
        """Refresh the file list for current path"""
        self.file_list.controls.clear()

        try:
            path = Path(self.current_path)

            # Update breadcrumb
            self._update_breadcrumb(path)

            # Get items in current directory
            items = []
            if path.exists() and path.is_dir():
                items = sorted(path.iterdir(), key=lambda x: (
                    not x.is_dir(), x.name))

            # Add parent directory link if not at root
            if str(path) != self.downloads_root:
                parent_item = ft.ListTile(
                    leading=ft.Icon(ft.Icons.ARROW_BACK, color="blue"),
                    title=ft.Text(".. (Parent Directory)",
                                  weight=ft.FontWeight.BOLD),
                    on_click=lambda e: self._navigate_to_parent(),
                )
                self.file_list.controls.append(parent_item)

            # Add directories and files
            for item in items:
                if item.is_dir():
                    # Directory
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.Icons.FOLDER, color="orange700"),
                        title=ft.Text(item.name),
                        subtitle=self._get_folder_info(item),
                        on_click=lambda e, p=item: self._navigate_to_folder(p),
                    )
                    self.file_list.controls.append(tile)
                elif item.suffix.lower() == '.pdf':
                    # PDF file
                    size_mb = item.stat().st_size / (1024 * 1024)
                    tile = ft.ListTile(
                        leading=ft.Icon(ft.Icons.PICTURE_AS_PDF, color="red"),
                        title=ft.Text(item.name, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{size_mb:.2f} MB"),
                        on_click=lambda e, p=item: self._view_pdf(p),
                        selected=self.selected_pdf == str(
                            item) if self.selected_pdf else False,
                    )
                    self.file_list.controls.append(tile)
                else:
                    # Other file
                    icon = self._get_file_icon(item.suffix)
                    size_kb = item.stat().st_size / 1024
                    tile = ft.ListTile(
                        leading=ft.Icon(icon, color="grey"),
                        title=ft.Text(item.name),
                        subtitle=ft.Text(f"{size_kb:.2f} KB"),
                    )
                    self.file_list.controls.append(tile)

            if not items:
                self.file_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "Empty folder", italic=True, color="grey"),
                        padding=20,
                    )
                )

        except Exception as e:
            self.file_list.controls.append(
                ft.Text(f"Error: {str(e)}", color="red")
            )

        self.page.update()

    def _update_breadcrumb(self, path: Path):
        """Update breadcrumb navigation"""
        self.breadcrumb.controls.clear()

        # Get path parts relative to downloads_root
        try:
            relative = path.relative_to(self.downloads_root)
            parts = [self.downloads_root] + list(relative.parts)
        except ValueError:
            parts = [str(path)]

        # Create breadcrumb items
        for i, part in enumerate(parts):
            if i > 0:
                self.breadcrumb.controls.append(
                    ft.Text("›", color="grey", size=14)
                )

            # Build full path for this part
            if i == 0:
                full_path = self.downloads_root
                display_name = "📁 Downloads"
            else:
                full_path = os.path.join(self.downloads_root, *parts[1:i+1])
                display_name = part

            btn = ft.TextButton(
                display_name,
                on_click=lambda e, p=full_path: self._navigate_to(p),
            )
            self.breadcrumb.controls.append(btn)

    def _navigate_to(self, path: str):
        """Navigate to a specific path"""
        self.current_path = path
        self._refresh_file_list()

    def _navigate_to_folder(self, folder_path: Path):
        """Navigate to a folder"""
        self.current_path = str(folder_path)
        self._refresh_file_list()

    def _navigate_to_parent(self):
        """Navigate to parent directory"""
        path = Path(self.current_path)
        if path.parent != path:
            self.current_path = str(path.parent)
            self._refresh_file_list()

    def _view_pdf(self, pdf_path: Path):
        """View a PDF file"""
        self.selected_pdf = str(pdf_path)

        # Get file info
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        import time
        modified_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(pdf_path.stat().st_mtime))

        # Update PDF viewer with file info and open button
        self.pdf_viewer.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, color="red", size=40),
                ft.Column([
                    ft.Text(pdf_path.name, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{size_mb:.2f} MB", size=14, color="grey"),
                    ft.Text(f"Modified: {modified_time}",
                            size=12, color="grey"),
                ], spacing=2),
            ], spacing=15),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DESCRIPTION, size=100, color="blue400"),
                    ft.Text("PDF Preview", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{pdf_path.name}", size=14, color="grey"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Open PDF in Default Viewer",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=lambda e: self._open_file(pdf_path),
                        style=ft.ButtonStyle(
                            bgcolor="blue",
                            color="white",
                        ),
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Click the button to open this PDF in your system's default PDF viewer",
                        size=12,
                        color="grey",
                        text_align=ft.TextAlign.CENTER,
                        italic=True,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                alignment=ft.alignment.center,
            ),
        ], spacing=10, expand=True)

        self._refresh_file_list()  # Refresh to update selection
        self.page.update()

    def _open_file(self, file_path: Path):
        """Open file in default system application"""
        import subprocess
        import sys

        try:
            if sys.platform == 'win32':
                os.startfile(str(file_path))
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(file_path)])
            else:  # linux
                subprocess.run(['xdg-open', str(file_path)])
        except Exception as e:
            # Show error dialog
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error opening file: {str(e)}"),
                bgcolor="red",
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _get_folder_info(self, folder_path: Path) -> ft.Text:
        """Get folder information"""
        try:
            items = list(folder_path.iterdir())
            pdf_count = sum(
                1 for item in items if item.suffix.lower() == '.pdf')
            folder_count = sum(1 for item in items if item.is_dir())

            info_parts = []
            if pdf_count > 0:
                info_parts.append(
                    f"{pdf_count} PDF{'s' if pdf_count != 1 else ''}")
            if folder_count > 0:
                info_parts.append(
                    f"{folder_count} folder{'s' if folder_count != 1 else ''}")

            return ft.Text(", ".join(info_parts) if info_parts else "Empty")
        except:
            return ft.Text("Unknown")

    def _get_file_icon(self, extension: str):
        """Get icon for file type"""
        ext_lower = extension.lower()
        icon_map = {
            '.pdf': ft.Icons.PICTURE_AS_PDF,
            '.jpg': ft.Icons.IMAGE,
            '.jpeg': ft.Icons.IMAGE,
            '.png': ft.Icons.IMAGE,
            '.gif': ft.Icons.IMAGE,
            '.docx': ft.Icons.DESCRIPTION,
            '.doc': ft.Icons.DESCRIPTION,
            '.txt': ft.Icons.TEXT_SNIPPET,
        }
        return icon_map.get(ext_lower, ft.Icons.INSERT_DRIVE_FILE)
