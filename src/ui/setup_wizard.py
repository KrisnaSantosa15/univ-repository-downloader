"""
Setup Wizard for Skripsi Downloader
Handles initial configuration via terminal prompts
"""
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def run_setup_wizard():
    """
    Run the initial setup wizard to get document info from user

    Returns:
        dict: Configuration with cookie, document_id, and document_title
    """
    console.clear()

    # Banner
    console.print(Panel(
        "[bold cyan]🚀 Skripsi Downloader - Setup Wizard[/bold cyan]\n\n"
        "[yellow]Let's configure your download![/yellow]",
        border_style="cyan"
    ))
    console.print()

    # Get Document Title
    console.print("[bold green]Step 1: Document Information[/bold green]")
    document_title = Prompt.ask(
        "[cyan]Enter the document title[/cyan]\n(This will be used for folder and PDF names)",
        default="My Thesis"
    )
    console.print()

    # Get Document ID
    console.print("[bold green]Step 2: Document ID[/bold green]")
    console.print("[dim]The document ID can be found in the URL:[/dim]")
    console.print(
        "[dim]Example: https://reader-repository.upi.edu/[yellow]130155[/yellow][/dim]")
    document_id = Prompt.ask(
        "[cyan]Enter the document ID[/cyan]",
        default="130155"
    )
    console.print()

    # Get Cookie
    console.print("[bold green]Step 3: Authentication Cookie[/bold green]")
    console.print("[dim]How to get your cookie:[/dim]")
    console.print("[dim]1. Open the document page in your browser[/dim]")
    console.print("[dim]2. Press F12 to open Developer Tools[/dim]")
    console.print(
        "[dim]3. Go to Application → Cookies → reader-repository.upi.edu[/dim]")
    console.print("[dim]4. Copy the value of 'cf_clearance' cookie[/dim]")
    console.print("[dim]   OR in Console tab, type: document.cookie[/dim]")
    console.print()

    use_browser = Confirm.ask(
        "[cyan]Do you want to use browser automation to get cookie?[/cyan]",
        default=True
    )

    cookie_string = ""
    if use_browser:
        try:
            from src.core.browser_automation import get_cookies_from_browser, test_cookies

            console.print()
            console.print("[cyan]🌐 Starting browser automation...[/cyan]")
            cookie_string = get_cookies_from_browser(document_id)

            if cookie_string:
                # Test the cookies
                if test_cookies(cookie_string, document_id):
                    console.print(
                        "[bold green]✓ Cookies validated successfully![/bold green]")
                else:
                    console.print(
                        "[yellow]⚠️  Cookies might not be working. You can try again later.[/yellow]")
            else:
                console.print(
                    "[yellow]⚠️  Failed to get cookies from browser.[/yellow]")
                console.print(
                    "[yellow]Let's try manual entry instead...[/yellow]")
                console.print()
                cookie_string = Prompt.ask(
                    "[cyan]Paste your cookie string here[/cyan]")
        except ImportError:
            console.print("[red]✗ Browser automation not available.[/red]")
            console.print(
                "[yellow]Please install: pip install selenium webdriver-manager[/yellow]")
            console.print()
            cookie_string = Prompt.ask(
                "[cyan]Paste your cookie string here[/cyan]")
        except Exception as e:
            console.print(f"[red]✗ Error with browser automation: {e}[/red]")
            console.print("[yellow]Falling back to manual entry...[/yellow]")
            console.print()
            cookie_string = Prompt.ask(
                "[cyan]Paste your cookie string here[/cyan]")
    else:
        cookie_string = Prompt.ask(
            "[cyan]Paste your cookie string here[/cyan]")

    console.print()

    # Confirmation
    console.print(Panel(
        f"[bold]Configuration Summary:[/bold]\n\n"
        f"📄 Document Title: [cyan]{document_title}[/cyan]\n"
        f"🆔 Document ID: [cyan]{document_id}[/cyan]\n"
        f"🍪 Cookie: [cyan]{cookie_string[:50]}...[/cyan]",
        title="[bold green]✓ Setup Complete[/bold green]",
        border_style="green"
    ))
    console.print()

    return {
        'document_title': document_title,
        'document_id': document_id,
        'cookie_string': cookie_string
    }


def save_config_to_file(config_data):
    """Save configuration to a file for future use"""
    config_file = "download_config.txt"

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(f"DOCUMENT_TITLE={config_data['document_title']}\n")
        f.write(f"DOCUMENT_ID={config_data['document_id']}\n")
        f.write(f"COOKIE={config_data['cookie_string']}\n")

    console.print(f"[dim]Configuration saved to {config_file}[/dim]\n")


def load_config_from_file():
    """Load configuration from file if exists"""
    config_file = "download_config.txt"

    if not os.path.exists(config_file):
        return None

    config_data = {}
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                if key == 'DOCUMENT_TITLE':
                    config_data['document_title'] = value
                elif key == 'DOCUMENT_ID':
                    config_data['document_id'] = value
                elif key == 'COOKIE':
                    config_data['cookie_string'] = value

    return config_data if config_data else None
