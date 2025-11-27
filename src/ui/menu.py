"""
Menu Module for Skripsi Downloader
Beautiful terminal UI using Rich and Questionary
"""
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from .menu_auto import download_menu_auto

console = Console()


class MenuSystem:
    """Beautiful terminal menu system"""

    def __init__(self, config, downloader, converter):
        self.config = config
        self.downloader = downloader
        self.converter = converter

    def show_banner(self):
        """Display application banner"""
        console.clear()
        banner = Text()
        banner.append(
            "╔═══════════════════════════════════════════════════╗\n", style="bold cyan")
        banner.append(
            "║                                                   ║\n", style="bold cyan")
        banner.append("║        ", style="bold cyan")
        banner.append("SKRIPSI DOWNLOADER & CONVERTER", style="bold yellow")
        banner.append("        ║\n", style="bold cyan")
        banner.append(
            "║                                                   ║\n", style="bold cyan")
        banner.append("║           ", style="bold cyan")
        banner.append("Universitas Pendidikan Indonesia", style="bold green")
        banner.append("        ║\n", style="bold cyan")
        banner.append(
            "║                                                   ║\n", style="bold cyan")
        banner.append(
            "╚═══════════════════════════════════════════════════╝", style="bold cyan")
        console.print(banner)
        console.print()

    def show_main_menu(self):
        """Display main menu and get user choice"""
        table = Table(
            show_header=False,
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 2)
        )
        table.add_column("Option", style="bold yellow")
        table.add_column("Description", style="white")

        table.add_row("📥 Download", "Download chapters from repository")
        table.add_row("📄 Convert", "Convert downloaded images to PDF/DOCX")
        table.add_row("⚙️  Settings", "Configure application settings")
        table.add_row("ℹ️  Info", "View current configuration")
        table.add_row("🚪 Exit", "Exit the application")

        console.print(
            Panel(table, title="[bold white]Main Menu[/bold white]", border_style="cyan"))
        console.print()

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Download chapters",
                "Convert images to PDF/DOCX",
                "Settings",
                "View info",
                "Exit"
            ],
            style=questionary.Style([
                ("selected", "fg:cyan bold"),
                ("pointer", "fg:cyan bold"),
                ("highlighted", "fg:cyan"),
            ])
        ).ask()

        return choice

    def download_menu(self):
        """Download menu with auto-detection"""
        download_menu_auto(self)

    def convert_menu(self):
        """Convert menu"""
        console.print(Panel(
            "[bold cyan]Convert Images[/bold cyan]",
            border_style="cyan"
        ))
        console.print()

        # Check for available chapters (scan all directories)
        chapters = []
        chapter_dirs = {}

        if os.path.exists(self.config.output_dir):
            for item in os.listdir(self.config.output_dir):
                item_path = os.path.join(self.config.output_dir, item)
                if os.path.isdir(item_path):
                    # Check if it has images
                    images = [f for f in os.listdir(item_path)
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                    if images:
                        if item.startswith("chapter_"):
                            chapter_num = item.split("_")[1]
                            display_name = f"Chapter {chapter_num}"
                            chapters.append(display_name)
                            chapter_dirs[display_name] = item
                        else:
                            chapters.append(item)
                            chapter_dirs[item] = item

        if not chapters:
            console.print("[yellow]No downloaded chapters found![/yellow]")
            console.print("[yellow]Please download chapters first.[/yellow]\n")
            questionary.press_any_key_to_continue(
                "Press any key to continue...").ask()
            return

        chapter = questionary.select(
            "Select chapter to convert:",
            choices=chapters + ["← Back to main menu"]
        ).ask()

        if chapter == "← Back to main menu":
            return

        output_format = questionary.select(
            "Select output format:",
            choices=[
                "PDF (Fast, preserves images)",
                "DOCX with OCR (Slow, extracts text)",
                "Both",
                "← Back"
            ]
        ).ask()

        if output_format == "← Back":
            return

        # Get image files
        chapter_dir_name = chapter_dirs[chapter]
        chapter_dir = self.config.get_chapter_dir(chapter_dir_name)
        image_files = []
        for file in os.listdir(chapter_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_files.append(os.path.join(chapter_dir, file))

        if not image_files:
            console.print(
                "[red]No image files found in chapter directory![/red]\n")
            questionary.press_any_key_to_continue(
                "Press any key to continue...").ask()
            return

        console.print(
            f"\n[green]Found {len(image_files)} image files[/green]\n")

        # Perform conversion
        output_base = chapter_dir_name.upper().replace("_", "")

        if "PDF" in output_format or "Both" in output_format:
            output_path = os.path.join(
                self.config.output_dir, f"{output_base}.pdf")
            self.converter.images_to_pdf(image_files, output_path)

        if "DOCX" in output_format or "Both" in output_format:
            output_path = os.path.join(
                self.config.output_dir, f"{output_base}.docx")
            self.converter.images_to_docx(image_files, output_path)

        questionary.press_any_key_to_continue(
            "\nPress any key to continue...").ask()

    def settings_menu(self):
        """Settings menu"""
        console.print(Panel(
            "[bold cyan]Settings[/bold cyan]",
            border_style="cyan"
        ))
        console.print()

        setting = questionary.select(
            "What would you like to configure?",
            choices=[
                "Set document ID",
                "Set authentication cookie",
                "Change output directory",
                "Change OCR language",
                "← Back to main menu"
            ]
        ).ask()

        if setting == "← Back to main menu":
            return

        if "document ID" in setting:
            doc_id = questionary.text(
                "Enter document ID (e.g., 130155):",
                default=self.config.document_id
            ).ask()

            if doc_id:
                self.config.set_document_id(doc_id)
                console.print(
                    "[green]✓ Document ID updated successfully![/green]\n")

        elif "cookie" in setting:
            cookie = questionary.text(
                "Enter authentication cookie:",
                default=self.config.cookie_string
            ).ask()

            if cookie:
                self.config.set_cookie(cookie)
                console.print(
                    "[green]✓ Cookie updated successfully![/green]\n")

        elif "output directory" in setting:
            output_dir = questionary.text(
                "Enter output directory path:",
                default=self.config.output_dir
            ).ask()

            if output_dir:
                self.config.set_output_dir(output_dir)
                console.print(
                    "[green]✓ Output directory updated successfully![/green]\n")

        elif "OCR language" in setting:
            language = questionary.text(
                "Enter OCR language code (e.g., 'ind' for Indonesian, 'eng' for English):",
                default=self.config.ocr_language
            ).ask()

            if language:
                self.config.set_ocr_language(language)
                console.print(
                    "[green]✓ OCR language updated successfully![/green]\n")

        questionary.press_any_key_to_continue(
            "Press any key to continue...").ask()

    def info_menu(self):
        """Display current configuration info"""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="cyan"
        )
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Mask cookie for security
        cookie_display = self.config.cookie_string[:20] + "..." if len(
            self.config.cookie_string) > 20 else self.config.cookie_string

        table.add_row("Document ID", self.config.document_id)
        table.add_row("Output Directory", self.config.output_dir)
        table.add_row("Authentication Cookie", cookie_display)
        table.add_row("OCR Language", self.config.ocr_language)
        table.add_row("Request Timeout", f"{self.config.timeout} seconds")
        table.add_row("Delay Between Requests",
                      f"{self.config.delay_between_requests} seconds")

        console.print()
        console.print(Panel(
            table, title="[bold white]Current Configuration[/bold white]", border_style="cyan"))
        console.print()

        # Show available chapters (scan all chapter_* directories)
        available_chapters = []
        if os.path.exists(self.config.output_dir):
            for item in os.listdir(self.config.output_dir):
                item_path = os.path.join(self.config.output_dir, item)
                if os.path.isdir(item_path):
                    # Count image files
                    image_files = len([f for f in os.listdir(item_path)
                                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
                    if image_files > 0:
                        # Format chapter name nicely
                        if item.startswith("chapter_"):
                            chapter_num = item.split("_")[1]
                            available_chapters.append(
                                f"Chapter {chapter_num}: {image_files} images")
                        else:
                            available_chapters.append(
                                f"{item}: {image_files} images")

        if available_chapters:
            chapters_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.ROUNDED,
                border_style="green"
            )
            chapters_table.add_column("Downloaded Chapters", style="green")

            for chapter in available_chapters:
                chapters_table.add_row(chapter)

            console.print(Panel(
                chapters_table, title="[bold white]Available Content[/bold white]", border_style="green"))
            console.print()
        else:
            console.print(Panel(
                "[yellow]No chapters downloaded yet[/yellow]",
                title="[bold white]Available Content[/bold white]",
                border_style="yellow"
            ))
            console.print()

        questionary.press_any_key_to_continue(
            "Press any key to continue...").ask()

    def run(self):
        """Main menu loop"""
        while True:
            self.show_banner()
            choice = self.show_main_menu()

            if not choice or choice == "Exit":
                console.print(Panel(
                    "[bold green]Thank you for using Skripsi Downloader![/bold green]",
                    border_style="green"
                ))
                break
            elif "Download" in choice:
                self.download_menu()
            elif "Convert" in choice:
                self.convert_menu()
            elif "Settings" in choice:
                self.settings_menu()
            elif "info" in choice:
                self.info_menu()
