"""
Download Page - Interface for downloading chapters with progress tracking
"""
import flet as ft
import threading
import os
from pathlib import Path
from PyPDF2 import PdfMerger
from src.core.downloader import ImageDownloader
import time


class DownloadPage(ft.Container):
    """Download page with auto-detection and progress tracking"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.page = main_window.page

        # Get fresh config reference
        self.config = main_window.config

        # Create downloader with current config
        self.downloader = ImageDownloader(self.config)

        # State
        self.is_downloading = False
        self.detected_chapters = []

        # Build UI
        self._build_ui()
        self.expand = True
        self.padding = 20

    def did_mount(self):
        """Called after the page is added to the view"""
        self._refresh_config_display()

    def _refresh_config_display(self):
        """Refresh the config display and recreate downloader with updated config"""
        # Refresh config reference from main window
        self.config = self.main_window.config

        # Recreate downloader with fresh config
        self.downloader = ImageDownloader(self.config)

        # Update UI text controls if they exist
        if hasattr(self, 'doc_title_text'):
            self.doc_title_text.value = self.config.document_title

        if hasattr(self, 'doc_id_text'):
            self.doc_id_text.value = self.config.document_id

        if hasattr(self, 'doc_output_text'):
            self.doc_output_text.value = self.config.output_dir

    def _build_ui(self):
        """Build the download page UI"""
        # Title
        title = ft.Text(
            "📥 Download Chapters",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # Document info card - store references for updates
        self.doc_title_text = ft.Text(self.config.document_title)
        self.doc_id_text = ft.Text(self.config.document_id)
        self.doc_output_text = ft.Text(self.config.output_dir, italic=True)

        doc_info = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color="blue"),
                        ft.Text("Current Document",
                                weight=ft.FontWeight.BOLD, size=16),
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("Title:", weight=ft.FontWeight.BOLD),
                        self.doc_title_text,
                    ]),
                    ft.Row([
                        ft.Text("ID:", weight=ft.FontWeight.BOLD),
                        self.doc_id_text,
                    ]),
                    ft.Row([
                        ft.Text("Output:", weight=ft.FontWeight.BOLD),
                        self.doc_output_text,
                    ]),
                ], spacing=8),
                padding=20,
            ),
        )

        # Download mode tabs
        self.download_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Auto-detect All",
                    icon=ft.Icons.AUTO_MODE,
                    content=self._build_auto_mode(),
                ),
                ft.Tab(
                    text="Specific Chapter",
                    icon=ft.Icons.FILTER_1,
                    content=self._build_specific_mode(),
                ),
                ft.Tab(
                    text="Manual Mode",
                    icon=ft.Icons.EDIT,
                    content=self._build_manual_mode(),
                ),
            ],
        )

        # Layout
        self.content = ft.Column(
            [
                title,
                doc_info,
                ft.Divider(height=20),
                self.download_tabs,
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_auto_mode(self):
        """Build auto-detect all chapters UI"""
        # Detect button
        detect_btn = ft.ElevatedButton(
            "🔍 Detect Available Chapters",
            icon=ft.Icons.SEARCH,
            on_click=self._on_detect_chapters,
            disabled=False,
        )

        # Detected chapters display
        self.chapters_display = ft.Container(
            content=ft.Text(
                "Click 'Detect' to find available chapters", italic=True),
            bgcolor="grey100",
            padding=15,
            border_radius=10,
        )

        # Download all button
        self.download_all_btn = ft.ElevatedButton(
            "📥 Download All Detected Chapters",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._on_download_all,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor="green700",
                color="white",
            ),
        )

        # Progress section
        self.progress_bar = ft.ProgressBar(value=0, width=600, visible=False)
        self.progress_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        self.status_text = ft.Text("", size=12, color="grey700")

        # Log output
        self.log_list = ft.ListView(
            spacing=5,
            height=200,
            auto_scroll=True,
        )

        self.log_container = ft.Container(
            content=self.log_list,
            bgcolor="black",
            padding=10,
            border_radius=10,
            visible=False,
        )

        return ft.Container(
            content=ft.Column([
                detect_btn,
                ft.Divider(),
                ft.Text("Detected Chapters:", weight=ft.FontWeight.BOLD),
                self.chapters_display,
                self.download_all_btn,
                ft.Divider(height=20),
                self.progress_text,
                self.progress_bar,
                self.status_text,
                ft.Divider(),
                self.log_container,
            ], spacing=10),
            padding=20,
        )

    def _build_specific_mode(self):
        """Build specific chapter download UI"""
        self.specific_chapter_field = ft.TextField(
            label="Chapter Number",
            hint_text="e.g., 1",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        download_specific_btn = ft.ElevatedButton(
            "📥 Download Chapter",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._on_download_specific,
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Enter the chapter number you want to download:", size=14),
                self.specific_chapter_field,
                download_specific_btn,
                ft.Text("The page limit will be auto-detected.",
                        italic=True, size=12),
            ], spacing=15),
            padding=20,
        )

    def _build_manual_mode(self):
        """Build manual download mode UI"""
        self.manual_chapter_field = ft.TextField(
            label="Chapter Number",
            hint_text="e.g., 1",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.manual_start_page_field = ft.TextField(
            label="Start Page",
            hint_text="e.g., 0",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="0",
        )

        self.manual_end_page_field = ft.TextField(
            label="End Page",
            hint_text="e.g., 50",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        download_manual_btn = ft.ElevatedButton(
            "📥 Download Range",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._on_download_manual,
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Manually specify chapter and page range:", size=14),
                ft.Row([
                    self.manual_chapter_field,
                    self.manual_start_page_field,
                    self.manual_end_page_field,
                ], spacing=10),
                download_manual_btn,
                ft.Text("⚠️ Use this mode only if auto-detection fails.",
                        italic=True, size=12, color="orange700"),
            ], spacing=15),
            padding=20,
        )

    def _on_detect_chapters(self, e):
        """Detect available chapters"""
        self.chapters_display.content = ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("Detecting chapters...", size=14),
        ])
        self.page.update()

        # Run detection in thread
        def detect():
            try:
                self.detected_chapters = self.downloader.detect_available_chapters()

                # Update UI
                if self.detected_chapters:
                    chips = [
                        ft.Chip(
                            label=ft.Text(f"Chapter {ch}"),
                            leading=ft.Icon(
                                ft.Icons.CHECK_CIRCLE, color="green"),
                        ) for ch in self.detected_chapters
                    ]

                    self.chapters_display.content = ft.Column([
                        ft.Text(f"✅ Found {len(self.detected_chapters)} chapters:",
                                weight=ft.FontWeight.BOLD, color="green"),
                        ft.Row(chips, wrap=True, spacing=5),
                    ])
                    self.download_all_btn.disabled = False
                else:
                    self.chapters_display.content = ft.Text(
                        "❌ No chapters found. Check your cookies and document ID.",
                        color="red",
                    )
                    self.download_all_btn.disabled = True

                self.page.update()
            except Exception as ex:
                self.chapters_display.content = ft.Text(
                    f"❌ Error: {str(ex)}",
                    color="red",
                )
                self.page.update()

        thread = threading.Thread(target=detect, daemon=True)
        thread.start()

    def _on_download_all(self, e):
        """Download all detected chapters"""
        if not self.detected_chapters:
            return

        self._start_download_process(self.detected_chapters)

    def _on_download_specific(self, e):
        """Download specific chapter"""
        if not self.specific_chapter_field.value:
            return

        try:
            chapter = int(self.specific_chapter_field.value)
            self._start_download_process([chapter])
        except ValueError:
            pass

    def _on_download_manual(self, e):
        """Download with manual range"""
        try:
            chapter = int(self.manual_chapter_field.value)
            start_page = int(self.manual_start_page_field.value or 0)
            end_page = int(self.manual_end_page_field.value)

            # For manual mode, we'll need to implement a different method
            self._add_log(
                f"Manual download: Chapter {chapter}, Pages {start_page}-{end_page}")
            self._add_log("Manual mode download not yet implemented")
        except ValueError:
            self._add_log("Invalid input values")

    def _start_download_process(self, chapters: list):
        """Start the download process in a background thread"""
        if self.is_downloading:
            return

        self.is_downloading = True
        self.log_container.visible = True
        self.progress_bar.visible = True
        self.log_list.controls.clear()

        def download_worker():
            try:
                total_chapters = len(chapters)
                chapter_pdfs = []

                for idx, chapter in enumerate(chapters):
                    # Update progress
                    progress = (idx / total_chapters) * 100
                    self.progress_bar.value = progress / 100
                    self.progress_text.value = f"Downloading Chapter {chapter} ({idx + 1}/{total_chapters})"
                    self._add_log(f"📥 Starting Chapter {chapter}...")
                    self.page.update()

                    # Download chapter with auto-detection
                    result = self.downloader.download_chapter_auto(chapter)

                    if result:
                        self._add_log(
                            f"✅ Chapter {chapter} completed!", "green")

                        # Look for the chapter PDF
                        chapter_dir = self.config.get_chapter_dir(
                            f"chapter_{chapter}")
                        chapter_pdf = os.path.join(
                            chapter_dir, f"Chapter_{chapter}.pdf")
                        if os.path.exists(chapter_pdf):
                            chapter_pdfs.append(chapter_pdf)
                    else:
                        self._add_log(f"❌ Chapter {chapter} failed!", "red")

                    self.page.update()

                # Create combined PDF from all chapter PDFs
                if chapter_pdfs and len(chapter_pdfs) > 1:
                    self._add_log(f"📚 Creating combined PDF...", "blue")
                    self.page.update()

                    combined_success = self._create_combined_pdf(chapter_pdfs)
                    if combined_success:
                        self._add_log(f"✅ Combined PDF created!", "green")
                    else:
                        self._add_log(
                            f"⚠️ Combined PDF creation failed", "orange700")

                    self.page.update()

                # Complete
                self.progress_bar.value = 1.0
                self.progress_text.value = f"✅ Download Complete! Downloaded {total_chapters} chapters"
                self.progress_text.color = "green700"
                self._add_log(
                    f"🎉 All done! Check: {self.config.output_dir}", "green")
                self._add_log(
                    f"📁 Redirecting to Files page...", "blue")
                self.page.update()

                # Redirect to Files page after 2 seconds
                time.sleep(2)
                self.main_window._navigate_to("files")

            except Exception as ex:
                self._add_log(f"❌ Error: {str(ex)}", "red")
            finally:
                self.is_downloading = False
                self.page.update()

        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()

    def _add_log(self, message: str, color="white"):
        """Add a log message"""
        self.log_list.controls.append(
            ft.Text(message, size=12, color=color)
        )
        if len(self.log_list.controls) > 100:
            self.log_list.controls.pop(0)
        self.page.update()

    def _create_combined_pdf(self, chapter_pdfs: list) -> bool:
        """Create a single PDF combining all chapter PDFs"""
        try:
            # Sort PDFs by chapter number
            chapter_pdfs.sort()

            # Output file in document folder
            document_title = self.config.document_title
            output_pdf = os.path.join(
                self.config.output_dir, f"{document_title}.pdf")

            merger = PdfMerger()

            for pdf_path in chapter_pdfs:
                self._add_log(
                    f"  Adding {os.path.basename(pdf_path)}...", "grey")
                merger.append(pdf_path)

            merger.write(output_pdf)
            merger.close()

            self._add_log(f"  Saved: {os.path.basename(output_pdf)}", "cyan")
            return True

        except Exception as e:
            self._add_log(f"  Error: {str(e)}", "red")
            return False
