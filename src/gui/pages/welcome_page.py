"""
Welcome Page - Initial setup wizard for first-time users
"""
import flet as ft
from src.core.browser_automation import get_cookies_from_browser


class WelcomePage(ft.Container):
    """Welcome page with setup wizard"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config = main_window.config
        self.page = main_window.page

        # Build UI
        self._build_ui()
        self.expand = True
        self.padding = 40

    def _build_ui(self):
        """Build the welcome page UI"""
        # Title
        title = ft.Text(
            "🎓 Welcome to UPI Repository Downloader",
            size=32,
            weight=ft.FontWeight.BOLD,
            color="blue900",
        )

        subtitle = ft.Text(
            "Let's set up your configuration to get started",
            size=16,
            color="grey700",
        )

        # Document title input
        self.doc_title_field = ft.TextField(
            label="Document Title",
            hint_text="e.g., My Thesis - Chapter Analysis",
            value=self.config.document_title,
            width=500,
            autofocus=True,
        )

        # Document ID input
        self.doc_id_field = ft.TextField(
            label="Document ID",
            hint_text="e.g., 130155",
            value=self.config.document_id,
            width=500,
        )

        # Document ID help
        doc_id_help = ft.Container(
            content=ft.Column([
                ft.Text("📖 How to find Document ID:",
                        weight=ft.FontWeight.BOLD),
                ft.Text("1. Go to the document page on reader-repository.upi.edu"),
                ft.Text(
                    "2. Look at the URL: https://reader-repository.upi.edu/[ID]"),
                ft.Text("3. Copy the ID number"),
            ], spacing=5),
            bgcolor="blue50",
            padding=15,
            border_radius=10,
            width=500,
        )

        # Cookie method selection
        self.cookie_method = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="browser",
                         label="🤖 Browser Automation (Easy - Recommended)"),
                ft.Radio(value="manual", label="✍️ Manual Cookie Entry"),
            ]),
            value="browser",
        )

        # Manual cookie fields (initially hidden)
        self.manual_cookie_container = ft.Container(
            content=ft.Column([
                ft.TextField(
                    label="cf_clearance",
                    hint_text="Paste cf_clearance cookie value",
                    width=500,
                    visible=False,
                ),
                ft.TextField(
                    label="PHPSESSID",
                    hint_text="Paste PHPSESSID cookie value",
                    width=500,
                    visible=False,
                ),
            ], spacing=10),
            visible=False,
        )

        # Status message
        self.status_text = ft.Text("", color="blue700")

        # Progress indicator
        self.progress = ft.ProgressRing(visible=False, width=30, height=30)

        # Buttons
        get_cookies_btn = ft.ElevatedButton(
            "🚀 Get Started",
            icon=ft.Icons.ROCKET_LAUNCH,
            on_click=self._on_get_started,
            style=ft.ButtonStyle(
                bgcolor="blue700",
                color="white",
                padding=20,
            ),
        )

        skip_btn = ft.TextButton(
            "Skip Setup (Use Defaults)",
            on_click=self._on_skip,
        )

        # Layout
        self.content = ft.Column(
            [
                title,
                subtitle,
                ft.Divider(height=30),
                ft.Text("📝 Step 1: Document Information",
                        size=20, weight=ft.FontWeight.BOLD),
                self.doc_title_field,
                self.doc_id_field,
                doc_id_help,
                ft.Divider(height=30),
                ft.Text("🔐 Step 2: Authentication",
                        size=20, weight=ft.FontWeight.BOLD),
                self.cookie_method,
                self.manual_cookie_container,
                ft.Divider(height=30),
                ft.Row([
                    get_cookies_btn,
                    skip_btn,
                ], spacing=10),
                ft.Row([self.progress, self.status_text], spacing=10),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )

    def _on_get_started(self, e):
        """Handle get started button click"""
        # Validate inputs
        if not self.doc_title_field.value or not self.doc_id_field.value:
            self._show_error(
                "Please fill in both Document Title and Document ID")
            return

        # Update config
        self.config.document_title = self.doc_title_field.value
        self.config.document_id = self.doc_id_field.value

        # Get cookies
        if self.cookie_method.value == "browser":
            self._get_cookies_from_browser()
        else:
            self._get_cookies_manual()

    def _get_cookies_from_browser(self):
        """Get cookies using browser automation"""
        self.progress.visible = True
        self.status_text.value = "Opening browser to extract cookies..."
        self.status_text.color = "blue700"
        self.page.update()

        try:
            # Update config with current form values FIRST
            self.config.document_title = self.doc_title_field.value
            self.config.document_id = self.doc_id_field.value

            # Update output directory based on new title
            import os
            self.config.output_dir = os.path.join(
                "downloaded",
                self.config._sanitize_filename(self.config.document_title)
            )

            # Use browser automation
            cookie_string = get_cookies_from_browser(self.config.document_id)

            if cookie_string:
                # Cookie string is already formatted
                self.config.cookie_string = cookie_string

                # Save config with ALL updated values
                self.main_window.save_config()

                # Reload config in main window to ensure it's fresh
                self.main_window.reload_config()

                # Success
                self.progress.visible = False
                self.status_text.value = "✅ Setup complete! Redirecting to Download page..."
                self.status_text.color = "green700"
                self.page.update()

                # Navigate to download page after 1 second
                import time
                time.sleep(1)
                self.main_window._navigate_to("download")
            else:
                self._show_error(
                    "Failed to extract cookies. Please try manual method.")
        except Exception as ex:
            self._show_error(f"Browser automation failed: {str(ex)}")
        finally:
            self.progress.visible = False
            self.page.update()

    def _get_cookies_manual(self):
        """Get cookies from manual input"""
        self._show_error(
            "Manual cookie entry not yet implemented in GUI. Use browser automation.")

    def _on_skip(self, e):
        """Skip setup and use defaults"""
        # Save current values
        if self.doc_title_field.value:
            self.config.document_title = self.doc_title_field.value
        if self.doc_id_field.value:
            self.config.document_id = self.doc_id_field.value

        self.main_window.save_config()
        self.main_window._navigate_to("download")

    def _show_error(self, message: str):
        """Show error message"""
        self.progress.visible = False
        self.status_text.value = f"❌ {message}"
        self.status_text.color = "red700"
        self.page.update()
