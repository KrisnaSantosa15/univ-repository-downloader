"""
Settings Page - Configure application settings
"""
import flet as ft
from src.core.browser_automation import get_cookies_from_browser


class SettingsPage(ft.Container):
    """Settings page for application configuration"""

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
        """Build the settings page UI"""
        title = ft.Text(
            "⚙️ Settings",
            size=28,
            weight=ft.FontWeight.BOLD,
        )

        # Document Settings Section
        doc_settings_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color="blue"),
                        ft.Text("Document Settings",
                                weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    self._build_document_settings(),
                ]),
                padding=20,
            ),
        )

        # Authentication Settings Section
        auth_settings_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LOCK, color="orange"),
                        ft.Text("Authentication",
                                weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    self._build_auth_settings(),
                ]),
                padding=20,
            ),
        )

        # OCR Settings Section
        ocr_settings_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TEXT_FIELDS, color="green"),
                        ft.Text("OCR Settings",
                                weight=ft.FontWeight.BOLD, size=18),
                    ]),
                    ft.Divider(),
                    self._build_ocr_settings(),
                ]),
                padding=20,
            ),
        )

        # Save button
        save_btn = ft.ElevatedButton(
            "💾 Save Settings",
            icon=ft.Icons.SAVE,
            on_click=self._on_save_settings,
            style=ft.ButtonStyle(
                bgcolor="blue700",
                color="white",
                padding=20,
            ),
        )

        self.status_message = ft.Text("", size=14)

        # Layout
        self.content = ft.Column(
            [
                title,
                ft.Divider(),
                doc_settings_card,
                auth_settings_card,
                ocr_settings_card,
                ft.Divider(height=20),
                save_btn,
                self.status_message,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

    def _build_document_settings(self):
        """Build document settings UI"""
        self.doc_title_field = ft.TextField(
            label="Document Title",
            value=self.config.document_title,
            width=500,
        )

        self.doc_id_field = ft.TextField(
            label="Document ID",
            value=self.config.document_id,
            width=300,
        )

        self.output_dir_field = ft.TextField(
            label="Output Directory",
            value=self.config.output_dir,
            width=500,
            read_only=True,
            helper_text="Auto-generated based on document title",
        )

        return ft.Column([
            self.doc_title_field,
            self.doc_id_field,
            self.output_dir_field,
        ], spacing=15)

    def _build_auth_settings(self):
        """Build authentication settings UI"""
        cookie_status = "✅ Configured" if self.config.cookie_string != "empty" else "❌ Not configured"
        cookie_color = "green" if self.config.cookie_string != "empty" else "red"

        self.cookie_status_text = ft.Text(
            f"Cookie Status: {cookie_status}",
            color=cookie_color,
            weight=ft.FontWeight.BOLD,
        )

        update_cookies_btn = ft.ElevatedButton(
            "🤖 Update Cookies (Browser Automation)",
            icon=ft.Icons.REFRESH,
            on_click=self._on_update_cookies,
        )

        self.cookie_progress = ft.ProgressRing(
            visible=False, width=30, height=30)
        self.cookie_message = ft.Text("", size=12)

        return ft.Column([
            self.cookie_status_text,
            ft.Text("Cookies expire periodically and need to be refreshed",
                    size=12, italic=True, color="grey700"),
            ft.Row([update_cookies_btn, self.cookie_progress]),
            self.cookie_message,
        ], spacing=10)

    def _build_ocr_settings(self):
        """Build OCR settings UI"""
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

        return ft.Column([
            self.ocr_lang_dropdown,
            ft.Text("Used for DOCX conversion with text extraction",
                    size=12, italic=True, color="grey700"),
        ], spacing=10)

    def _on_save_settings(self, e):
        """Save settings"""
        try:
            # Update config
            self.config.document_title = self.doc_title_field.value
            self.config.document_id = self.doc_id_field.value
            self.config.ocr_language = self.ocr_lang_dropdown.value

            # Update output directory based on new title
            import os
            self.config.output_dir = os.path.join(
                "downloaded",
                self.config._sanitize_filename(self.config.document_title)
            )
            self.output_dir_field.value = self.config.output_dir

            # Save to file
            self.main_window.save_config()

            # Show success message
            self.status_message.value = "✅ Settings saved successfully!"
            self.status_message.color = "green700"
            self.page.update()

        except Exception as ex:
            self.status_message.value = f"❌ Error: {str(ex)}"
            self.status_message.color = "red700"
            self.page.update()

    def _on_update_cookies(self, e):
        """Update cookies using browser automation"""
        self.cookie_progress.visible = True
        self.cookie_message.value = "Opening browser..."
        self.cookie_message.color = "blue700"
        self.page.update()

        def update_worker():
            try:
                cookie_string = get_cookies_from_browser(
                    self.config.document_id)

                if cookie_string:
                    # Cookie string is already formatted
                    self.config.cookie_string = cookie_string
                    self.main_window.save_config()

                    # Update UI
                    self.cookie_status_text.value = "Cookie Status: ✅ Configured"
                    self.cookie_status_text.color = "green"
                    self.cookie_message.value = "✅ Cookies updated successfully!"
                    self.cookie_message.color = "green700"
                else:
                    self.cookie_message.value = "❌ Failed to extract cookies"
                    self.cookie_message.color = "red700"

            except Exception as ex:
                self.cookie_message.value = f"❌ Error: {str(ex)}"
                self.cookie_message.color = "red700"
            finally:
                self.cookie_progress.visible = False
                self.page.update()

        import threading
        thread = threading.Thread(target=update_worker, daemon=True)
        thread.start()
