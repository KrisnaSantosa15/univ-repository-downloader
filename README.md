# 📚 UPI Repository Downloader


<center><img src="documentation/user-journey.png" alt="User Journey" width="300"></center>

A beautiful, modular Python application for downloading and converting thesis chapters from Universitas Pendidikan Indonesia (UPI) repository.

## ✨ Features

<center><img src="documentation/features.png" alt="Features" width="300"></center>

- 🎨 **Beautiful GUI** - Modern Material Design 3 interface with file explorer and PDF viewer
- 🖥️ **Terminal UI** - Classic command-line interface for power users
- 🤖 **Auto-detect chapters and pages** - No manual counting needed
- 🌐 **Browser automation** - Automatic cookie extraction
- 📥 **Flexible downloads** - Download all, specific, or manual ranges
- 📄 **Multiple formats** - PDF (fast) or DOCX with OCR (text extraction)
- 📁 **File Management** - Built-in file explorer with PDF preview
- 🔄 **Combined PDFs** - Automatically creates master PDF from all chapters

## 🚀 Quick Start

### Option 1: Use the Executable (Easiest - Windows Only)

**No Python installation required!**

#### 📥 Download & Install

Choose your preferred version:

**🎨 GUI Version (Recommended for most users)**
1. **Go to [Releases](https://github.com/KrisnaSantosa15/univ-repository-downloader/releases/latest)**
2. **Download** `UPI-Repository-Downloader-GUI-v4.0.0-windows.zip` (~82 MB)
3. **Extract** the ZIP file to any location (e.g., `C:\Tools\UPI-Downloader-GUI`)
4. **Double-click** `UPI-Repository-Downloader-GUI.exe`
5. **Enjoy** the beautiful Material Design interface!

**Features:**
- ✨ Modern, intuitive interface
- 📁 Built-in file explorer with folder navigation
- 📄 PDF viewer with file info and open button
- 🎯 Visual progress tracking
- 🖱️ Point-and-click operation

**🖥️ CLI Version (For power users & servers)**
1. **Go to [Releases](https://github.com/KrisnaSantosa15/univ-repository-downloader/releases/latest)**
2. **Download** `UPI-Repository-Downloader-CLI-v4.0.0-windows.zip` (~51 MB)
3. **Extract** the ZIP file to any location (e.g., `C:\Tools\UPI-Downloader-CLI`)
4. **Double-click** `UPI-Repository-Downloader.exe`
5. **Follow** the terminal setup wizard

**Features:**
- ⚡ Lightweight and fast
- 💻 Perfect for remote servers
- 🎯 Keyboard-driven workflow
- 📊 Detailed console output

**Windows Security Warning:** When you first run the EXE, Windows may show *"Windows protected your PC"*. This is normal for unsigned applications. Click **"More info"** → **"Run anyway"**.

#### 📋 What's Included

<center><img src="documentation/gui.png" alt="User Journey" width="300"></center>

Both executable packages include:
- ✅ Python runtime (no installation needed)
- ✅ All required libraries bundled
- ✅ Complete documentation
- ✅ Ready to run - just extract and double-click!

**Optional (for advanced features):**
- Chrome browser - For automatic cookie extraction
- Tesseract OCR - For DOCX conversion with text extraction

[📦 Download Latest Release](https://github.com/KrisnaSantosa15/univ-repository-downloader/releases/latest) | [📖 Full Release Guide](dev/guides/GITHUB_RELEASE_GUIDE.md)

---

### Option 2: Run from Source (For Developers / All Platforms)

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

#### Installation Steps

1. **Clone or Download the Repository**
```bash
git clone https://github.com/KrisnaSantosa15/univ-repository-downloader.git
cd univ-repository-downloader
```
Or download as ZIP from GitHub and extract.

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **(Optional) Install Tesseract OCR**
For DOCX conversion with text extraction:
- **Windows**: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
- **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-ind`
- **macOS**: `brew install tesseract tesseract-lang`

4. **Run the Application**

**GUI Version (with beautiful interface):**
```bash
python main_gui.py
```

**CLI Version (terminal interface):**
```bash
python main.py
```

## 📖 Usage

### 🎨 GUI Version

#### Navigation
The GUI features 6 main pages accessible via the left sidebar:

1. **🏠 Home (Welcome)** - First-run setup wizard
   - Enter document title and ID
   - Browser automation for cookies
   - Quick start guide

2. **📥 Download** - Download chapters with progress tracking
   - **Auto-detect All**: Finds all chapters automatically
   - **Specific Chapter**: Select one chapter
   - **Manual Mode**: Specify exact ranges
   - Real-time progress bars
   - Download logs

3. **📁 Files** - File explorer with PDF viewer
   - Navigate all downloaded documents
   - Browse chapter folders
   - View PDF files with file info
   - Open PDFs in default viewer
   - Shows combined PDFs and individual chapters

4. **🔄 Convert** - Convert images to PDF/DOCX
   - Select folder to convert
   - Choose output format
   - Progress tracking

5. **⚙️ Settings** - Configure application
   - Update document ID
   - Refresh cookies with browser automation
   - OCR language settings

6. **ℹ️ Info** - View app information
   - Current configuration
   - Downloaded chapters
   - Developer credits
   - Feature list

#### First Run
1. Launch the GUI
2. Enter **Document Title** and **Document ID**
3. Click **"Get Started with Browser"** (or manual cookie entry)
4. Browser opens automatically → you log in
5. Cookies extracted automatically
6. Start downloading!

### 🖥️ CLI Version

#### First Run - Setup Wizard
The terminal app will guide you through:
1. **Document Title** - Enter the thesis name
2. **Document ID** - Find it in the URL: `https://reader-repository.upi.edu/[ID]`

![Document Id Screenshot](documentation/document-id.png)

3. **Authentication** - Choose browser automation (easy) or manual cookie entry

Your settings are saved to `download_config.txt` for next time.

![Setup Wizard Screenshot](documentation/setup-wizard.png)

#### Main Menu Options

**📥 Download**
- **Auto-detect all**: Finds and downloads all chapters automatically
- **Select specific**: Pick one chapter with auto page detection
- **Manual mode**: Specify exact chapter and page numbers

![Download Menu Screenshot](documentation/main-menu.png)

![Download Options Screenshot](documentation/auto-downloader.png)

![Download Progress Screenshot](documentation/checking-chapters.png)

![Completed Download Screenshot](documentation/completed.png)

**📄 Convert**
Convert downloaded images to:
- PDF (preserves image quality)
- DOCX with OCR (extracts text - Indonesian/English)

**⚙️ Settings**
Update document ID, cookies, output folder, or OCR language

**ℹ️ Info**
View current configuration and downloaded chapters

## 📁 Output Structure

```
downloaded/
└── [Your Document Title]/
    ├── chapter_1/
    │   └── page_000.jpg, page_001.jpg...
    ├── chapter_2/...
    ├── Chapter_1.pdf
    ├── Chapter_2.pdf
    └── [Document Title].pdf  ← Combined PDF
```

## 🔧 Getting Cookies (if not using browser automation)

1. Log in to https://reader-repository.upi.edu/
2. Press `F12` → Go to **Application** tab
3. Navigate to **Cookies** → `reader-repository.upi.edu`
4. Copy values of `cf_clearance` and `PHPSESSID`
5. Paste into the setup wizard

## 🛠️ Utility Scripts

- **Check dependencies**: `python scripts/check_dependencies.py`

## 📁 Project Structure

The project follows a professional modular structure:

```
univ-repository-downloader/
├── main.py              # CLI entry point
├── main_gui.py          # GUI entry point
├── src/                 # Source code
│   ├── config/         # Configuration
│   ├── core/           # Core logic (download, convert)
│   ├── ui/             # Terminal UI components
│   └── gui/            # GUI components (Flet)
│       ├── main_window.py      # Navigation & routing
│       └── pages/              # GUI pages
│           ├── welcome_page.py
│           ├── download_page.py
│           ├── files_page.py
│           ├── convert_page.py
│           ├── settings_page.py
│           └── info_page.py
├── build_exe.spec      # PyInstaller spec for CLI
├── build_gui.spec      # PyInstaller spec for GUI
├── scripts/            # Utility scripts
├── documentation/      # Screenshots & docs
├── releases/           # Release packages
└── downloaded/         # Output directory
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed documentation.

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| No chapters found | Update cookies (they expire!) |
| Browser automation fails | Install Chrome or use manual cookie entry |
| OCR not working | Install Tesseract and add to PATH |
| Download fails | Get fresh cookies using browser automation |

## 🤝 Contributing

Want to improve this tool? Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Commit** your changes: `git commit -m 'Add feature'`
4. **Push** to branch: `git push origin feature-name`
5. **Submit** a pull request

### Code Guidelines
- Follow PEP 8 style
- Add comments for complex logic
- Test before submitting
- Keep user experience smooth

### Adapting for Other Repositories
Modify these files:
- `src/config/config.py` - Update URL patterns
- `src/core/downloader.py` - Adjust chapter detection
- `src/core/browser_automation.py` - Update cookie requirements

## ⚠️ Legal & Ethics

**For personal educational use only.**

✅ Do:
- Use for your own research/study
- Respect rate limits (built-in delays)
- Have legitimate access to documents

❌ Don't:
- Share or distribute downloaded content
- Overwhelm servers with requests
- Violate copyright laws
- Share your `download_config.txt` (contains session cookies)

## 📜 License

Educational use only. Use responsibly and ethically.

## 🙏 Acknowledgments

Built with these amazing tools:
- [Flet](https://flet.dev/) - Beautiful cross-platform GUI framework
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal UI
- [Questionary](https://github.com/tmbo/questionary) - Interactive prompts
- [Selenium](https://www.selenium.dev/) - Browser automation
- [PyInstaller](https://pyinstaller.org/) - Executable packaging
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Text extraction
- [img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) - Fast PDF creation
- [PyPDF2](https://github.com/py-pdf/PyPDF2) - PDF manipulation
- [python-docx](https://github.com/python-openxml/python-docx) - DOCX generation

**Developed by [Krisna Santosa](https://github.com/KrisnaSantosa15)** 💜

Special thanks to **UPI (Universitas Pendidikan Indonesia)** for their repository system.

---
