"""
Downloader Module for Skripsi Downloader
Handles downloading of images from UPI repository
"""
import os
import time
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

console = Console()


class ImageDownloader:
    """Class to handle downloading images from repository"""

    def __init__(self, config):
        self.config = config
        self.downloaded_files = []

    def detect_available_chapters(self):
        """
        Auto-detect available chapters for the document

        Returns:
            list: List of available chapter numbers
        """
        console.print(
            "\n[bold cyan]🔍 Detecting available chapters...[/bold cyan]\n")
        available_chapters = []

        # Test chapters 0-10 (usually documents have 1-7 chapters)
        for chapter_num in range(0, 11):
            url = self.config.get_chapter_url("img", chapter_num, "0")

            try:
                response = requests.get(
                    url,
                    headers=self.config.headers,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )

                # Check if it's an error page (only for HTML responses)
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")

                    # Only check for error messages if it's HTML, not an image
                    if "text/html" in content_type:
                        content_str = response.content.decode(
                            'utf-8', errors='ignore')
                        if "PHP Error" in content_str or "str_replace()" in content_str:
                            console.print(
                                f"[dim]Chapter {chapter_num}: Not available[/dim]")
                            continue
                        elif "ImagickException" in content_str or "Failed to read" in content_str:
                            console.print(
                                f"[dim]Chapter {chapter_num}: Not available[/dim]")
                            continue

                    # Check if response is an image
                    is_image = (
                        "image" in content_type or
                        (isinstance(response.content, bytes) and len(response.content) > 8 and (
                            # JPEG (check first 3 bytes)
                            response.content[:3] == b'\xff\xd8\xff' or
                            # PNG (first 8 bytes)
                            response.content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
                        ))
                    )

                    if is_image:
                        available_chapters.append(chapter_num)
                        console.print(
                            f"[green]✓ Chapter {chapter_num}: Available[/green]")

            except Exception as e:
                console.print(
                    f"[dim]Chapter {chapter_num}: Error checking ({str(e)[:50]})[/dim]")
                continue

            time.sleep(0.1)  # Small delay

        console.print(
            f"\n[bold green]Found {len(available_chapters)} available chapters: {available_chapters}[/bold green]\n")
        return available_chapters

    def detect_chapter_page_limit(self, chapter_num):
        """
        Auto-detect the last page of a chapter using binary search

        Args:
            chapter_num: Chapter number to detect

        Returns:
            int: Last valid page number (0-indexed)
        """
        console.print(
            f"[bold cyan]🔍 Detecting page limit for Chapter {chapter_num}...[/bold cyan]")

        # Binary search for the last page
        left, right = 0, 1000  # Assume max 1000 pages
        last_valid = -1

        # First, find an upper bound
        test_page = 1
        while test_page <= right:
            if self._is_page_valid(chapter_num, test_page):
                last_valid = test_page
                test_page *= 2
            else:
                right = test_page
                break

        # If no valid page found at all
        if last_valid == -1:
            # Check page 0
            if self._is_page_valid(chapter_num, 0):
                left = 0
                right = 100
                last_valid = 0
            else:
                console.print(
                    f"[red]No valid pages found for Chapter {chapter_num}[/red]\n")
                return -1
        else:
            left = last_valid

        # Binary search for exact limit
        while left < right:
            mid = (left + right + 1) // 2

            if self._is_page_valid(chapter_num, mid):
                last_valid = mid
                left = mid
            else:
                right = mid - 1

            time.sleep(0.05)  # Small delay

        console.print(
            f"[bold green]✓ Chapter {chapter_num} has pages 0 to {last_valid} ({last_valid + 1} pages total)[/bold green]\n")
        return last_valid

    def _is_page_valid(self, chapter_num, page_num):
        """
        Check if a specific page exists

        Args:
            chapter_num: Chapter number
            page_num: Page number

        Returns:
            bool: True if page exists and is valid
        """
        url = self.config.get_chapter_url("img", chapter_num, page_num)

        try:
            response = requests.get(
                url,
                headers=self.config.headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )

            if response.status_code != 200:
                return False

            # Check if it's actually an image
            content_type = response.headers.get("Content-Type", "")

            # Only check for error messages if it's HTML, not an image
            if "text/html" in content_type:
                content_str = response.content.decode('utf-8', errors='ignore')
                if "ImagickException" in content_str or "Failed to read" in content_str:
                    return False
                if "PHP Error" in content_str:
                    return False
            is_image = (
                "image" in content_type or
                (len(response.content) > 8 and (
                    # JPEG (first 3 bytes)
                    response.content[:3] == b'\xff\xd8\xff' or
                    # PNG (first 8 bytes)
                    response.content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
                ))
            )

            return is_image

        except Exception:
            return False

    def download_page(self, base_url_img, base_url_file, page_number):
        """
        Download a single page

        Args:
            base_url_img: Primary URL pattern (img)
            base_url_file: Fallback URL pattern (file)
            page_number: Page number to download

        Returns:
            tuple: (success, content, filename) or (False, None, None)
        """
        tried_urls = [f"{base_url_img}{page_number}",
                      f"{base_url_file}{page_number}"]

        for url in tried_urls:
            try:
                response = requests.get(
                    url,
                    headers=self.config.headers,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )

                if response.status_code == 200 and response.content:
                    content_type = response.headers.get("Content-Type", "")

                    # Check if content is actually an image
                    is_image = (
                        "image" in content_type or
                        (len(response.content) > 8 and (
                            response.content[:3] == b'\xff\xd8\xff' or  # JPEG
                            # PNG (first 8 bytes)
                            response.content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
                        ))
                    )

                    if is_image:
                        # Determine file extension
                        filename = self._get_filename(
                            page_number, response.content)
                        return True, response.content, filename

            except requests.exceptions.RequestException as e:
                console.print(f"[yellow]Request error for {url}: {e}[/yellow]")
                continue

        return False, None, None

    def _get_filename(self, page_number, content):
        """Determine filename based on content type"""
        if content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            return f"page_{page_number:03d}.png"
        elif content[:2] == b'BM':
            return f"page_{page_number:03d}.bmp"
        else:
            return f"page_{page_number:03d}.jpg"

    def download_range(self, chapter_name, base_url_img, base_url_file, start_page, end_page):
        """
        Download a range of pages

        Args:
            chapter_name: Name of the chapter (e.g., 'bab2')
            base_url_img: Primary URL pattern
            base_url_file: Fallback URL pattern
            start_page: Starting page number
            end_page: Ending page number

        Returns:
            list: List of downloaded file paths
        """
        self.downloaded_files = []
        chapter_dir = self.config.get_chapter_dir(chapter_name)
        os.makedirs(chapter_dir, exist_ok=True)

        total_pages = end_page - start_page + 1
        success_count = 0
        failed_count = 0

        console.print(
            f"\n[bold cyan]Downloading {chapter_name.upper()}...[/bold cyan]")
        console.print(
            f"Pages: {start_page} to {end_page} ({total_pages} total)\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                f"[cyan]Downloading pages...",
                total=total_pages
            )

            for page_num in range(start_page, end_page + 1):
                success, content, filename = self.download_page(
                    base_url_img,
                    base_url_file,
                    page_num
                )

                if success:
                    filepath = os.path.join(chapter_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(content)
                    self.downloaded_files.append(filepath)
                    success_count += 1
                    progress.update(
                        task,
                        advance=1,
                        description=f"[green]Downloaded page {page_num}"
                    )
                else:
                    failed_count += 1
                    progress.update(
                        task,
                        advance=1,
                        description=f"[red]Failed page {page_num}"
                    )

                # Small delay to avoid overwhelming the server
                time.sleep(self.config.delay_between_requests)

        # Summary
        console.print(
            f"\n[bold green]✓ Success:[/bold green] {success_count} pages")
        if failed_count > 0:
            console.print(
                f"[bold red]✗ Failed:[/bold red] {failed_count} pages")

        return self.downloaded_files

    def download_chapter_auto(self, chapter_num):
        """
        Automatically download an entire chapter (auto-detect page limit)

        Args:
            chapter_num: Chapter number to download

        Returns:
            list: List of downloaded file paths
        """
        # Detect page limit
        last_page = self.detect_chapter_page_limit(chapter_num)

        if last_page < 0:
            console.print(
                f"[red]Cannot download Chapter {chapter_num}: No pages found[/red]\n")
            return []

        # Download using new URL format
        chapter_name = f"chapter_{chapter_num}"
        self.downloaded_files = []
        chapter_dir = self.config.get_chapter_dir(chapter_name)
        os.makedirs(chapter_dir, exist_ok=True)

        total_pages = last_page + 1
        success_count = 0
        failed_count = 0

        console.print(
            f"\n[bold cyan]Downloading Chapter {chapter_num}...[/bold cyan]")
        console.print(f"Pages: 0 to {last_page} ({total_pages} total)\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                "[cyan]Downloading pages...",
                total=total_pages
            )

            for page_num in range(0, last_page + 1):
                # Try both img and file modes
                url_img = self.config.get_chapter_url(
                    "img", chapter_num, page_num)
                url_file = self.config.get_chapter_url(
                    "file", chapter_num, page_num)

                success = False
                content = None

                for url in [url_img, url_file]:
                    try:
                        response = requests.get(
                            url,
                            headers=self.config.headers,
                            timeout=self.config.timeout,
                            verify=self.config.verify_ssl
                        )

                        if response.status_code == 200 and response.content:
                            content_type = response.headers.get(
                                "Content-Type", "")

                            # Check if it's an image
                            is_image = (
                                "image" in content_type or
                                (len(response.content) > 8 and (
                                    response.content[:3] == b'\xff\xd8\xff' or
                                    # PNG (first 8 bytes)
                                    response.content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
                                ))
                            )

                            if is_image:
                                content = response.content
                                success = True
                                break
                    except Exception:
                        continue

                if success and content:
                    filename = self._get_filename(page_num, content)
                    filepath = os.path.join(chapter_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(content)
                    self.downloaded_files.append(filepath)
                    success_count += 1
                    progress.update(
                        task,
                        advance=1,
                        description=f"[green]Downloaded page {page_num}"
                    )
                else:
                    failed_count += 1
                    progress.update(
                        task,
                        advance=1,
                        description=f"[red]Failed page {page_num}"
                    )

                time.sleep(self.config.delay_between_requests)

        # Summary
        console.print(
            f"\n[bold green]✓ Success:[/bold green] {success_count} pages")
        if failed_count > 0:
            console.print(
                f"[bold red]✗ Failed:[/bold red] {failed_count} pages")

        # Auto-create PDF for this chapter
        if self.downloaded_files:
            self._create_chapter_pdf(
                chapter_num, chapter_dir, self.downloaded_files)

        return self.downloaded_files

    def _create_chapter_pdf(self, chapter_num, chapter_dir, image_files):
        """Create PDF from chapter images"""
        import img2pdf

        if not image_files:
            return

        pdf_filename = f"Chapter_{chapter_num}.pdf"
        pdf_path = os.path.join(chapter_dir, pdf_filename)

        try:
            console.print(
                f"\n[cyan]📄 Creating PDF for Chapter {chapter_num}...[/cyan]")
            sorted_files = sorted(image_files)
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(sorted_files))
            console.print(f"[green]✓ PDF created: {pdf_filename}[/green]\n")
        except Exception as e:
            console.print(f"[red]✗ Failed to create PDF: {e}[/red]\n")

    def get_downloaded_files(self):
        """Get list of downloaded files"""
        return sorted(self.downloaded_files)
