"""
Convert Page - Interface for converting downloaded images to PDF/DOCX
"""
import flet as ft
import threading
import os
from src.core.converter import FileConverter


class ConvertPage(ft.Container):
    """Convert page for PDF and DOCX generation"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = main_window.config
        self.page = main_window.page
        self.converter = FileConverter(self.config)

        # State
        self.is_converting = False

        # Build UI
        self._build_ui()
        self.expand = True
        self.padding = 20

    def _build_ui(self):
        """Build the convert page UI"""
        title = ft.Text(
            "📄 Convert Images",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        subtitle = ft.Text(
            "Convert downloaded images to PDF or DOCX format",
            size=14,
            color="grey700",
        )

        # Check downloaded folders
        self.folders_list = self._get_downloaded_folders()

        # Folder selection
        self.folder_dropdown = ft.Dropdown(
            label="Select Chapter Folder",
            hint_text="Choose a folder to convert",
            options=[ft.dropdown.Option(
                f) for f in self.folders_list] if self.folders_list else [],
            width=500,
        )

        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh folders",
            on_click=self._on_refresh_folders,
        )

        # Conversion mode tabs
        convert_tabs = ft.Tabs(
            tabs=[
                ft.Tab(
                    text="PDF (Fast)",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    content=self._build_pdf_mode(),
                ),
                ft.Tab(
                    text="DOCX with OCR",
                    icon=ft.Icons.TEXT_FIELDS,
                    content=self._build_docx_mode(),
                ),
            ],
        )

        # Progress section
        self.progress_bar = ft.ProgressBar(value=0, width=600, visible=False)
        self.progress_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        self.status_text = ft.Text("", size=12, color="grey700")

        # Layout
        self.content = ft.Column(
            [
                title,
                subtitle,
                ft.Divider(height=20),
                ft.Row([
                    self.folder_dropdown,
                    refresh_btn,
                ]),
                ft.Divider(),
                convert_tabs,
                ft.Divider(height=20),
                self.progress_text,
                self.progress_bar,
                self.status_text,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_pdf_mode(self):
        """Build PDF conversion UI"""
        convert_btn = ft.ElevatedButton(
            "📄 Convert to PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self._on_convert_pdf,
            style=ft.ButtonStyle(
                bgcolor="red700",
                color="white",
            ),
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Convert images to PDF (preserves original quality)", size=14),
                ft.Text("✓ Fast conversion", size=12, color="green"),
                ft.Text("✓ High quality output", size=12, color="green"),
                ft.Text("✓ No OCR required", size=12, color="green"),
                ft.Divider(),
                convert_btn,
            ], spacing=10),
            padding=20,
        )

    def _build_docx_mode(self):
        """Build DOCX conversion UI"""
        self.ocr_lang_dropdown = ft.Dropdown(
            label="OCR Language",
            options=[
                ft.dropdown.Option("ind", "Indonesian"),
                ft.dropdown.Option("eng", "English"),
                ft.dropdown.Option("ind+eng", "Indonesian + English"),
            ],
            value=self.config.ocr_language,
            width=300,
        )

        convert_docx_btn = ft.ElevatedButton(
            "📝 Convert to DOCX",
            icon=ft.Icons.DESCRIPTION,
            on_click=self._on_convert_docx,
            style=ft.ButtonStyle(
                bgcolor="blue700",
                color="white",
            ),
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Convert images to DOCX with OCR text extraction", size=14),
                ft.Text("⚠️ Requires Tesseract OCR installed",
                        size=12, color="orange"),
                ft.Text("✓ Text is searchable and editable",
                        size=12, color="green"),
                ft.Text("✓ Preserves images", size=12, color="green"),
                ft.Divider(),
                self.ocr_lang_dropdown,
                convert_docx_btn,
            ], spacing=10),
            padding=20,
        )

    def _get_downloaded_folders(self):
        """Get list of downloaded chapter folders"""
        folders = []
        if os.path.exists(self.config.output_dir):
            for item in os.listdir(self.config.output_dir):
                item_path = os.path.join(self.config.output_dir, item)
                if os.path.isdir(item_path) and item.startswith("chapter_"):
                    folders.append(item)
        return sorted(folders)

    def _on_refresh_folders(self, e):
        """Refresh the folders list"""
        self.folders_list = self._get_downloaded_folders()
        self.folder_dropdown.options = [
            ft.dropdown.Option(f) for f in self.folders_list]
        self.folder_dropdown.value = None
        self.page.update()

    def _on_convert_pdf(self, e):
        """Convert to PDF"""
        if not self.folder_dropdown.value:
            self.status_text.value = "❌ Please select a folder first"
            self.status_text.color = "red"
            self.page.update()
            return

        self._start_conversion("pdf", self.folder_dropdown.value)

    def _on_convert_docx(self, e):
        """Convert to DOCX"""
        if not self.folder_dropdown.value:
            self.status_text.value = "❌ Please select a folder first"
            self.status_text.color = "red"
            self.page.update()
            return

        # Update OCR language in config
        if self.ocr_lang_dropdown.value:
            self.config.ocr_language = self.ocr_lang_dropdown.value

        self._start_conversion("docx", self.folder_dropdown.value)

    def _start_conversion(self, mode: str, folder: str):
        """Start conversion process"""
        if self.is_converting:
            return

        self.is_converting = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0

        def convert_worker():
            try:
                folder_path = os.path.join(self.config.output_dir, folder)

                self.progress_text.value = f"Converting {folder} to {mode.upper()}..."
                self.status_text.value = "Processing images..."
                self.status_text.color = "blue700"
                self.page.update()

                # Simulate progress (since converter doesn't provide progress callback)
                for i in range(5):
                    self.progress_bar.value = (i + 1) / 10
                    self.page.update()
                    import time
                    time.sleep(0.2)

                # Perform conversion
                if mode == "pdf":
                    success = self.converter.convert_images_to_pdf(folder_path)
                else:
                    success = self.converter.convert_images_to_docx_with_ocr(
                        folder_path)

                # Complete
                self.progress_bar.value = 1.0

                if success:
                    self.progress_text.value = f"✅ Conversion Complete!"
                    self.progress_text.color = "green700"
                    self.status_text.value = f"File saved in: {self.config.output_dir}"
                    self.status_text.color = "green"
                else:
                    self.progress_text.value = f"❌ Conversion Failed"
                    self.progress_text.color = "red700"
                    self.status_text.value = "Check if Tesseract is installed (for DOCX)"
                    self.status_text.color = "red"

            except Exception as ex:
                self.progress_text.value = f"❌ Error"
                self.progress_text.color = "red700"
                self.status_text.value = str(ex)
                self.status_text.color = "red"
            finally:
                self.is_converting = False
                self.page.update()

        thread = threading.Thread(target=convert_worker, daemon=True)
        thread.start()
