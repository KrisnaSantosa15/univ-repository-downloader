"""
Skripsi Downloader & Converter - Main Application
A modular, user-friendly tool for downloading and converting thesis chapters

Author: Refactored with beautiful UI
Version: 3.0
"""
import warnings
from rich.console import Console
from rich.prompt import Confirm
from config import Config
from downloader import ImageDownloader
from converter import FileConverter
from menu import MenuSystem
from setup_wizard import run_setup_wizard, save_config_to_file, load_config_from_file

# Suppress SSL warnings (since we're using verify=False)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

console = Console()


def main():
    """Main application entry point"""
    try:
        # Check if config exists
        saved_config = load_config_from_file()

        if saved_config:
            console.print(f"\n[green]✓ Found saved configuration:[/green]")
            console.print(
                f"  Document: [cyan]{saved_config['document_title']}[/cyan]")
            console.print(
                f"  ID: [cyan]{saved_config['document_id']}[/cyan]\n")

            use_saved = Confirm.ask("Use this configuration?", default=True)

            if not use_saved:
                saved_config = run_setup_wizard()
                save_config_to_file(saved_config)
        else:
            # Run setup wizard for first time
            saved_config = run_setup_wizard()
            save_config_to_file(saved_config)

        # Initialize configuration with wizard data
        config = Config(
            cookie_string=saved_config['cookie_string'],
            document_id=saved_config['document_id'],
            document_title=saved_config['document_title']
        )

        # Initialize modules
        downloader = ImageDownloader(config)
        converter = FileConverter(config)

        # Initialize and run menu system
        menu = MenuSystem(config, downloader, converter)
        menu.run()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nAn unexpected error occurred: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
