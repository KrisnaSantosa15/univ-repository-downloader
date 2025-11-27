"""
Info Page - Display application information and current configuration
"""
import flet as ft
import os


class InfoPage(ft.Container):
    """Info page showing app details and current config"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = main_window.config
        self.page = main_window.page

        # Build UI
        self._build_ui()
        self.expand = True
        self.padding = 20

    def _build_ui(self):
        """Build the info page UI"""
        title = ft.Text(
            "ℹ️ Information",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # App Info Card
        app_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, color="blue", size=40),
                        ft.Column([
                            ft.Text("UPI Repository Downloader",
                                    size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Version 1.0.0 (GUI)",
                                    size=14, color="grey700"),
                        ]),
                    ]),
                    ft.Divider(),
                    ft.Text("A beautiful, modular Python application for downloading and converting "
                            "thesis chapters from Universitas Pendidikan Indonesia (UPI) repository.",
                            size=14),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color="purple", size=20),
                        ft.Text("Developed by ", size=14),
                        ft.Text("Krisna Santosa", size=14,
                                weight=ft.FontWeight.BOLD, color="blue"),
                    ], spacing=5),
                    ft.Row([
                        ft.TextButton(
                            "🐙 GitHub",
                            icon=ft.Icons.CODE,
                            url="https://github.com/KrisnaSantosa15",
                        ),
                        ft.TextButton(
                            "📚 Documentation",
                            icon=ft.Icons.BOOK,
                            url="https://github.com/KrisnaSantosa15/univ-repository-downloader",
                        ),
                        ft.TextButton(
                            "🐛 Report Issue",
                            icon=ft.Icons.BUG_REPORT,
                            url="https://github.com/KrisnaSantosa15/univ-repository-downloader/issues",
                        ),
                    ], wrap=True),
                ]),
                padding=20,
            ),
        )

        # Current Config Card
        config_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color="orange"),
                        ft.Text("Current Configuration",
                                weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    self._build_config_table(),
                ]),
                padding=20,
            ),
        )

        # Downloaded Chapters Card
        chapters_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color="green"),
                        ft.Text("Downloaded Chapters",
                                weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    self._build_chapters_list(),
                ]),
                padding=20,
            ),
        )

        # Features Card
        features_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.STAR, color="amber"),
                        ft.Text("Features", weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self._build_feature_row(
                            "🤖", "Auto-detect chapters and pages"),
                        self._build_feature_row(
                            "🌐", "Browser automation for cookies"),
                        self._build_feature_row(
                            "📥", "Flexible download modes"),
                        self._build_feature_row("📄", "PDF & DOCX conversion"),
                        self._build_feature_row(
                            "🎨", "Beautiful Material Design UI"),
                        self._build_feature_row("⚡", "Fast and efficient"),
                    ], spacing=8),
                ]),
                padding=20,
            ),
        )

        # Layout
        self.content = ft.Column(
            [
                title,
                ft.Divider(),
                app_info_card,
                config_card,
                chapters_card,
                features_card,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_config_table(self):
        """Build configuration details table"""
        config_rows = [
            ["Document Title", self.config.document_title],
            ["Document ID", self.config.document_id],
            ["Output Directory", self.config.output_dir],
            ["Cookie Status", "✅ Configured" if self.config.cookie_string !=
                "empty" else "❌ Not configured"],
            ["OCR Language", self.config.ocr_language],
            ["Request Timeout", f"{self.config.timeout} seconds"],
            ["Request Delay", f"{self.config.delay_between_requests} seconds"],
        ]

        rows = []
        for label, value in config_rows:
            rows.append(
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            label, weight=ft.FontWeight.BOLD, size=14),
                        width=200,
                    ),
                    ft.Text(value, size=14, selectable=True),
                ], spacing=20)
            )

        return ft.Column(rows, spacing=10)

    def _build_chapters_list(self):
        """Build list of downloaded chapters"""
        if not os.path.exists(self.config.output_dir):
            return ft.Text("No downloads yet", italic=True, color="grey700")

        chapters = []
        for item in os.listdir(self.config.output_dir):
            item_path = os.path.join(self.config.output_dir, item)
            if os.path.isdir(item_path) and item.startswith("chapter_"):
                # Count images
                image_count = len([f for f in os.listdir(item_path)
                                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                chapters.append((item, image_count))

        if not chapters:
            return ft.Text("No chapters downloaded yet", italic=True, color="grey700")

        chapter_chips = [
            ft.Chip(
                label=ft.Text(f"{ch[0]} ({ch[1]} images)"),
                leading=ft.Icon(ft.Icons.FOLDER, color="blue"),
            ) for ch in sorted(chapters)
        ]

        return ft.Column([
            ft.Text(f"Total: {len(chapters)} chapters",
                    weight=ft.FontWeight.BOLD),
            ft.Row(chapter_chips, wrap=True, spacing=5),
        ])

    def _build_feature_row(self, icon: str, text: str):
        """Build a feature row"""
        return ft.Row([
            ft.Text(icon, size=20),
            ft.Text(text, size=14),
        ], spacing=10)
