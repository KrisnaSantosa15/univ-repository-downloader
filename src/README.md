# Source Code Structure

This directory contains the core source code for the UPI Repository Downloader, organized into logical modules.

## Directory Structure

```
src/
├── __init__.py           # Main package initialization
├── config/               # Configuration management
│   ├── __init__.py
│   └── config.py        # Config class with settings
├── core/                 # Core business logic
│   ├── __init__.py
│   ├── downloader.py    # Image downloading logic
│   ├── converter.py     # File conversion (PDF/DOCX)
│   └── browser_automation.py  # Cookie extraction via Selenium
└── ui/                   # User interface modules
    ├── __init__.py
    ├── menu.py          # Main menu system
    ├── menu_auto.py     # Auto-download menu helpers
    └── setup_wizard.py  # First-run configuration wizard
```

## Module Overview

### `config/`
Contains configuration management classes and settings.

- **`config.py`**: Central configuration class that manages:
  - Authentication cookies
  - Document IDs and titles
  - Output directories
  - HTTP headers and request settings
  - URL generation for chapters and pages

### `core/`
Contains the core business logic for downloading and converting files.

- **`downloader.py`**: Handles all download operations:
  - Auto-detects available chapters
  - Binary search for page limits
  - Downloads images with fallback URLs
  - Creates PDFs automatically
  
- **`converter.py`**: Manages file conversions:
  - Images to PDF (fast, preserves quality)
  - Images to DOCX with OCR (text extraction)
  
- **`browser_automation.py`**: Automates cookie extraction:
  - Opens browser using Selenium
  - Waits for user login
  - Captures session cookies
  - Validates cookies work

### `ui/`
Contains all user interface and interaction logic.

- **`menu.py`**: Main menu system with Rich UI:
  - Download options
  - Conversion menu
  - Settings management
  - Info display
  
- **`menu_auto.py`**: Download menu implementations:
  - Auto-detect all chapters
  - Select specific chapter
  - Manual download mode
  
- **`setup_wizard.py`**: First-run configuration:
  - Document title input
  - Document ID input
  - Cookie acquisition (auto or manual)
  - Config persistence

## Usage

Import modules using the package structure:

```python
from src.config import Config
from src.core import ImageDownloader, FileConverter
from src.ui import MenuSystem, run_setup_wizard
```

## Development

When adding new features:
1. Place core logic in `core/`
2. Place UI components in `ui/`
3. Place configuration in `config/`
4. Update `__init__.py` files to export new classes/functions
