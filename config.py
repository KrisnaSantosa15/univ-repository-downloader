"""
Configuration Module for Skripsi Downloader
Handles all configuration settings and constants
"""
import os


class Config:
    """Configuration class to store all application settings"""

    def __init__(self, cookie_string=None, document_id=None, document_title=None):
        # Authentication
        self.cookie_string = cookie_string or "empty"

        # Document information
        self.document_id = document_id or "130155"
        self.document_title = document_title or "My Thesis"

        # Base URL template
        self.base_url_template = "https://reader-repository.upi.edu/index.php/display/{mode}/{doc_id}/{chapter}/{page}"

        # Directory settings (use document title as parent folder)
        self.output_dir = os.path.join(
            "downloaded", self._sanitize_filename(self.document_title))

        # HTTP settings
        self.headers = {
            "Cookie": self.cookie_string,
            "User-Agent": "Mozilla/5.0 (compatible; script/1.0)"
        }

        # Download settings
        self.timeout = 20
        self.verify_ssl = False
        self.delay_between_requests = 0.2  # seconds

        # OCR settings
        self.ocr_language = "ind"  # Indonesian

    def get_chapter_url(self, mode, chapter, page):
        """
        Generate URL for a specific chapter and page

        Args:
            mode: 'img' or 'file'
            chapter: Chapter number
            page: Page number (optional, use empty string to omit)
        """
        if page == "":
            # For chapter detection (no page number)
            return f"https://reader-repository.upi.edu/index.php/display/{mode}/{self.document_id}/{chapter}"
        else:
            return f"https://reader-repository.upi.edu/index.php/display/{mode}/{self.document_id}/{chapter}/{page}"

    def set_cookie(self, cookie_string):
        """Update the cookie string"""
        self.cookie_string = cookie_string
        self.headers["Cookie"] = cookie_string

    def set_document_id(self, document_id):
        """Update the document ID"""
        self.document_id = str(document_id)

    def set_output_dir(self, output_dir):
        """Update the output directory"""
        self.output_dir = output_dir

    def set_ocr_language(self, language):
        """Update OCR language"""
        self.ocr_language = language

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def get_chapter_dir(self, chapter_name):
        """Get the full path for a chapter directory"""
        return os.path.join(self.output_dir, chapter_name)

    def _sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        import re
        # Remove invalid characters for Windows/Linux filenames
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        return sanitized or "document"
