"""
Auto-download helper methods for menu system
"""
import os
import time
import requests
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console
import questionary

console = Console()


def download_menu_auto(menu_self):
    """Enhanced download menu with auto-detection"""
    from rich.panel import Panel

    console.print(Panel(
        "[bold cyan]Download Options[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    download_mode = questionary.select(
        "How would you like to download?",
        choices=[
            "🤖 Auto-detect and download all chapters",
            "📋 Select specific chapter (auto-detect pages)",
            "✏️  Manual mode (specify chapter and pages)",
            "← Back to main menu"
        ]
    ).ask()

    if download_mode == "← Back to main menu":
        return

    menu_self.config.ensure_output_dir()

    if "Auto-detect and download all" in download_mode:
        download_all_auto(menu_self)

    elif "Select specific chapter" in download_mode:
        download_chapter_auto(menu_self)

    elif "Manual mode" in download_mode:
        download_manual(menu_self)

    questionary.press_any_key_to_continue(
        "\nPress any key to continue...").ask()


def download_all_auto(menu_self):
    """Auto-detect and download all available chapters"""
    console.print(
        f"\n[bold cyan]Document ID: {menu_self.config.document_id}[/bold cyan]\n")

    # Detect chapters
    chapters = menu_self.downloader.detect_available_chapters()

    if not chapters:
        console.print(
            "[red]No chapters found! Check your cookie and document ID.[/red]")
        return

    # Confirm download
    confirm = questionary.confirm(
        f"Download all {len(chapters)} chapters?",
        default=True
    ).ask()

    if not confirm:
        return

    # Download each chapter
    chapter_pdfs = []
    for chapter_num in chapters:
        menu_self.downloader.download_chapter_auto(chapter_num)
        # Collect chapter PDF path
        chapter_dir = menu_self.config.get_chapter_dir(
            f"chapter_{chapter_num}")
        pdf_path = os.path.join(chapter_dir, f"Chapter_{chapter_num}.pdf")
        if os.path.exists(pdf_path):
            chapter_pdfs.append(pdf_path)

    # Create combined PDF from all chapters
    if chapter_pdfs:
        _create_combined_pdf(menu_self, chapter_pdfs)


def download_chapter_auto(menu_self):
    """Let user select a chapter and auto-download with page detection"""
    console.print(
        f"\n[bold cyan]Document ID: {menu_self.config.document_id}[/bold cyan]\n")

    # Detect chapters
    chapters = menu_self.downloader.detect_available_chapters()

    if not chapters:
        console.print(
            "[red]No chapters found! Check your cookie and document ID.[/red]")
        return

    # Let user select
    chapter_choices = [f"Chapter {ch}" for ch in chapters] + ["← Back"]
    selected = questionary.select(
        "Select chapter to download:",
        choices=chapter_choices
    ).ask()

    if selected == "← Back":
        return

    # Extract chapter number
    chapter_num = int(selected.split()[1])

    # Confirm
    confirm = questionary.confirm(
        f"Download Chapter {chapter_num} (with auto page detection)?",
        default=True
    ).ask()

    if confirm:
        menu_self.downloader.download_chapter_auto(chapter_num)


def download_manual(menu_self):
    """Manual download mode - user specifies everything"""
    # Get chapter number
    chapter_input = questionary.text(
        "Enter chapter number:",
        default="1",
        validate=lambda x: x.isdigit() or "Please enter a valid number"
    ).ask()

    if not chapter_input:
        return

    chapter_num = int(chapter_input)

    # Get page range
    start_page = questionary.text(
        "Start page number:",
        default="0",
        validate=lambda x: x.isdigit() or "Please enter a valid number"
    ).ask()

    if not start_page:
        return

    end_page = questionary.text(
        "End page number:",
        default="20",
        validate=lambda x: x.isdigit() or "Please enter a valid number"
    ).ask()

    if not end_page:
        return

    start_page = int(start_page)
    end_page = int(end_page)

    if start_page > end_page:
        console.print(
            "[red]Start page must be less than or equal to end page![/red]")
        return

    # Confirm download
    confirm = questionary.confirm(
        f"Download Chapter {chapter_num}, pages {start_page} to {end_page}?",
        default=True
    ).ask()

    if not confirm:
        return

    # Download using new method
    chapter_name = f"chapter_{chapter_num}"
    chapter_dir = menu_self.config.get_chapter_dir(chapter_name)
    os.makedirs(chapter_dir, exist_ok=True)

    # Use the simplified download
    console.print(
        f"\n[bold cyan]Downloading Chapter {chapter_num}...[/bold cyan]")
    console.print(f"Pages: {start_page} to {end_page}\n")

    downloaded = []
    success = 0
    failed = 0
    total = end_page - start_page + 1

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Downloading...", total=total)

        for page in range(start_page, end_page + 1):
            url_img = menu_self.config.get_chapter_url(
                "img", chapter_num, page)
            url_file = menu_self.config.get_chapter_url(
                "file", chapter_num, page)

            page_success = False
            for url in [url_img, url_file]:
                try:
                    resp = requests.get(url, headers=menu_self.config.headers,
                                        timeout=menu_self.config.timeout,
                                        verify=menu_self.config.verify_ssl)
                    if resp.status_code == 200:
                        ct = resp.headers.get("Content-Type", "")
                        if "image" in ct or (len(resp.content) > 8 and resp.content[:3] == b'\xff\xd8\xff'):
                            filename = f"page_{page:03d}.jpg"
                            if len(resp.content) >= 8 and resp.content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
                                filename = f"page_{page:03d}.png"

                            filepath = os.path.join(chapter_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(resp.content)
                            downloaded.append(filepath)
                            success += 1
                            page_success = True
                            progress.update(task, advance=1,
                                            description=f"[green]Downloaded page {page}")
                            break
                except Exception:
                    continue

            if not page_success:
                failed += 1
                progress.update(task, advance=1,
                                description=f"[red]Failed page {page}")

            time.sleep(menu_self.config.delay_between_requests)

    console.print(f"\n[bold green]✓ Success:[/bold green] {success} pages")
    if failed > 0:
        console.print(f"[bold red]✗ Failed:[/bold red] {failed} pages")


def _create_combined_pdf(menu_self, chapter_pdfs):
    """Create a single PDF combining all chapter PDFs"""
    from PyPDF2 import PdfMerger

    if not chapter_pdfs:
        return

    console.print(
        f"\n[bold cyan]📚 Creating combined PDF from {len(chapter_pdfs)} chapters...[/bold cyan]")

    # Sort PDFs by chapter number
    chapter_pdfs.sort()

    # Output file in parent directory (document folder)
    document_title = menu_self.config.document_title
    output_pdf = os.path.join(
        menu_self.config.output_dir, f"{document_title}.pdf")

    try:
        merger = PdfMerger()

        for pdf_path in chapter_pdfs:
            console.print(
                f"  [dim]Adding {os.path.basename(pdf_path)}...[/dim]")
            merger.append(pdf_path)

        merger.write(output_pdf)
        merger.close()

        console.print(f"\n[bold green]✓ Combined PDF created:[/bold green]")
        console.print(f"  [cyan]{output_pdf}[/cyan]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to create combined PDF: {e}[/red]\n")
