"""
Browser Automation Module for Cookie Extraction
Automatically opens browser, waits for user to login, and captures cookies
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_cookies_from_browser(document_id="130155", timeout=300):
    """
    Open browser, wait for user to login, and capture cookies

    Args:
        document_id: Document ID to open
        timeout: Maximum time to wait for login (seconds)

    Returns:
        str: Cookie string or None if failed
    """
    console.print()
    console.print(Panel(
        "[bold cyan]🌐 Browser Cookie Extraction[/bold cyan]\n\n"
        "[yellow]A browser window will open. Please:[/yellow]\n"
        "1. ✅ Log in to the repository\n"
        "2. ✅ Navigate to your document page\n"
        "3. ✅ Wait for the page to load completely\n"
        "4. ✅ The browser will close automatically and cookies will be captured!\n\n"
        "[dim]The browser will stay open for up to 5 minutes[/dim]",
        border_style="cyan"
    ))
    console.print()

    driver = None
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Initialize driver
        console.print("[cyan]🚀 Starting browser...[/cyan]")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the repository
        url = f"https://reader-repository.upi.edu/index.php/display/file/{document_id}"
        console.print(f"[cyan]📂 Opening: {url}[/cyan]")
        driver.get(url)

        console.print()
        console.print(Panel(
            "[bold green]✋ Please log in now![/bold green]\n\n"
            "[yellow]Steps:[/yellow]\n"
            "1. Complete the login process\n"
            "2. Make sure you can see the document\n"
            "3. Just leave the browser open\n\n"
            "[dim]Waiting for cookies...[/dim]",
            border_style="green"
        ))
        console.print()

        # Wait for user to login and navigate
        start_time = time.time()
        cookies_found = False

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Waiting for login...", total=None)

            while (time.time() - start_time) < timeout:
                # Check if we have the necessary cookies
                cookies = driver.get_cookies()
                cookie_dict = {cookie['name']: cookie['value']
                               for cookie in cookies}

                # Check for cf_clearance (Cloudflare) or PHPSESSID (session)
                if 'cf_clearance' in cookie_dict or 'PHPSESSID' in cookie_dict:
                    # Also check if we're not on a login page
                    current_url = driver.current_url
                    if 'login' not in current_url.lower() and 'sso' not in current_url.lower():
                        cookies_found = True
                        break

                time.sleep(2)
                elapsed = int(time.time() - start_time)
                progress.update(
                    task, description=f"[cyan]Waiting for login... ({elapsed}s)")

        if not cookies_found:
            console.print(
                "[red]⏱️  Timeout: No valid cookies found after login[/red]")
            return None

        # Extract all cookies
        cookies = driver.get_cookies()
        cookie_string = "; ".join(
            [f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        console.print()
        console.print(
            "[bold green]✓ Cookies captured successfully![/bold green]")
        console.print(f"[dim]Found {len(cookies)} cookies[/dim]")
        console.print()

        # Show important cookies
        important_cookies = ['cf_clearance', 'PHPSESSID', '_ga']
        found_important = []
        for cookie in cookies:
            if cookie['name'] in important_cookies:
                value_preview = cookie['value'][:50] + \
                    "..." if len(cookie['value']) > 50 else cookie['value']
                console.print(
                    f"  [green]✓[/green] {cookie['name']}: [cyan]{value_preview}[/cyan]")
                found_important.append(cookie['name'])

        if not found_important:
            console.print(
                "[yellow]⚠️  Warning: No critical cookies found. Login might not have worked.[/yellow]")

        console.print()

        # Keep browser open for a moment so user can see success
        console.print("[dim]Browser will close in 3 seconds...[/dim]")
        time.sleep(3)

        return cookie_string

    except Exception as e:
        console.print(f"[red]✗ Error during browser automation: {e}[/red]")
        console.print(
            "[yellow]Please try manual cookie entry instead.[/yellow]")
        return None

    finally:
        if driver:
            try:
                driver.quit()
                console.print("[dim]Browser closed[/dim]")
            except:
                pass


def test_cookies(cookie_string, document_id="130155"):
    """
    Test if captured cookies work

    Args:
        cookie_string: Cookie string to test
        document_id: Document ID to test with

    Returns:
        bool: True if cookies work, False otherwise
    """
    import requests

    url = f"https://reader-repository.upi.edu/index.php/display/img/{document_id}/1/0"
    headers = {
        "Cookie": cookie_string,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        console.print("[cyan]🧪 Testing cookies...[/cyan]")
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        # Check if we got an image (not HTML error page)
        content_type = response.headers.get("Content-Type", "")
        is_valid = "image" in content_type and response.status_code == 200

        if is_valid:
            console.print("[green]✓ Cookies are working![/green]")
        else:
            console.print(
                f"[yellow]⚠️  Cookies might not be working (Content-Type: {content_type})[/yellow]")

        return is_valid

    except Exception as e:
        console.print(f"[red]✗ Error testing cookies: {e}[/red]")
        return False


if __name__ == "__main__":
    # Test the module
    console.print("[bold]Testing Browser Cookie Extraction[/bold]\n")
    cookies = get_cookies_from_browser()

    if cookies:
        console.print(
            f"\n[green]Success! Got {len(cookies)} characters of cookies[/green]")
        test_cookies(cookies)
    else:
        console.print("\n[red]Failed to get cookies[/red]")
