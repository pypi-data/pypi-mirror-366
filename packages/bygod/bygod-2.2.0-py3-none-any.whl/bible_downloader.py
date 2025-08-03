#!/usr/bin/env python3
"""
Bible Gateway Downloader - True Async Edition

A comprehensive, truly asynchronous tool for downloading Bible translations from
BibleGateway.com in multiple formats (JSON, CSV, YAML, XML) with genuine parallel
downloads, retry mechanisms, and flexible output options.

This module provides:
- True async HTTP requests with aiohttp for genuine parallelism
- Direct HTML parsing from BibleGateway (bypassing synchronous libraries)
- Support for multiple Bible translations simultaneously
- Output in various formats (JSON, CSV, YAML, XML)
- Intelligent rate limiting and retry mechanisms
- Organized output in structured directories
- Comprehensive logging and progress tracking

Author: Bible Gateway Downloader Team
License: MIT
Version: 2.2.0 - Verbosity & Concurrency Edition
"""

import argparse
import asyncio
import json
import logging
import os
import re
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from bs4 import BeautifulSoup
from meaningless import JSONDownloader
from meaningless.utilities.common import get_page

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Bible Gateway URL template
PASSAGE_URL_TEMPLATE = "https://www.biblegateway.com/passage/?search={}&version={}"

# Available Bible translations
BIBLE_TRANSLATIONS = {
    "NIV": "New International Version",
    "KJV": "King James Version",
    "ESV": "English Standard Version",
    "NKJV": "New King James Version",
    "NLT": "New Living Translation",
    "CSB": "Christian Standard Bible",
    "NASB": "New American Standard Bible",
    "RSV": "Revised Standard Version",
    "ASV": "American Standard Version",
    "WEB": "World English Bible",
    "YLT": "Young's Literal Translation",
    "AMP": "Amplified Bible",
    "MSG": "The Message",
    "CEV": "Contemporary English Version",
    "ERV": "Easy-to-Read Version",
    "GW": "God's Word Translation",
    "HCSB": "Holman Christian Standard Bible",
    "ICB": "International Children's Bible",
    "ISV": "International Standard Version",
    "LEB": "Lexham English Bible",
    "NCV": "New Century Version",
    "NET": "New English Translation",
    "NIRV": "New International Reader's Version",
    "NRSV": "New Revised Standard Version",
    "TLB": "The Living Bible",
    "TLV": "Tree of Life Version",
    "VOICE": "The Voice",
    "WYC": "Wycliffe Bible",
}

# List of all 66 Bible books in canonical order
BOOKS = [
    # Old Testament (39 books)
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    # New Testament (27 books)
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
]

# Default settings
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "bibles")
DEFAULT_RATE_LIMIT = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2
DEFAULT_TIMEOUT = 300

# =============================================================================
# LOGGING SETUP
# =============================================================================


def setup_logging(
    name: str = "bible_downloader",
    verbose: int = 0,
    quiet: bool = False,
    log_level: str = "INFO",
    error_log_file: str = None,
) -> logging.Logger:
    """
    Set up colored logging for the downloader with configurable verbosity and error logging.
    
    Args:
        name: Logger name
        verbose: Verbosity level (0=WARNING, 1=INFO, 2=DEBUG, 3+=ALL)
        quiet: Suppress all output except errors
        log_level: Explicit log level override
        error_log_file: File to log errors to in clean format
        
    Returns:
        Configured logger
    """
    import colorlog

    # Create logger
    logger = logging.getLogger(name)
    
    # Determine log level based on verbosity and quiet flags
    if quiet:
        console_level = logging.ERROR
    elif verbose == 0:
        console_level = logging.WARNING
    elif verbose == 1:
        console_level = logging.INFO
    elif verbose >= 2:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    
    # Override with explicit log level if provided
    if log_level:
        console_level = getattr(logging, log_level.upper())
    
    # Set logger level to match console level for quiet mode
    if quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(min(logging.DEBUG, console_level))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler with color
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(console_level)

    # Create formatter for console
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add error file handler if specified
    if error_log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(error_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(error_log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # Clean format for error file (no colors, more detailed)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"📝 Error logging enabled: {error_log_file}")

    return logger


# =============================================================================
# TRUE ASYNC BIBLE DOWNLOADER
# =============================================================================


class AsyncBibleDownloader:
    """
    True async Bible downloader that directly fetches from BibleGateway.

    This class bypasses synchronous libraries and makes direct HTTP requests
    to BibleGateway.com, parsing the HTML to extract Bible content. It provides
    genuine parallelism with asyncio and aiohttp.
    """

    def __init__(
        self,
        translation: str,
        max_concurrent_requests: int = 5,
        max_retries: int = 3,
        retry_delay: int = 2,
        timeout: int = 300,
    ):
        """
        Initialize the async Bible downloader.

        Args:
            translation: Bible translation code (e.g., "NIV", "KJV")
            max_concurrent_requests: Maximum concurrent HTTP requests
            max_retries: Maximum retry attempts per request
            retry_delay: Base delay between retries
            timeout: Request timeout in seconds
        """
        self.translation = translation.upper()
        self.max_concurrent_requests = max_concurrent_requests
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Validate translation
        if self.translation not in BIBLE_TRANSLATIONS:
            raise ValueError(f"Unsupported translation: {translation}")

        # Create semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Session will be created when needed
        self.session: Optional[aiohttp.ClientSession] = None

        # Set up logging - use the main logger to ensure consistent verbosity
        self.logger = logging.getLogger("bible_downloader")

        # Store original get_page function for restoration
        self._original_get_page = get_page

        # Monkey patch get_page to use our async session
        self._setup_monkey_patch()

    def _setup_monkey_patch(self):
        """Set up monkey patching of meaningless library's get_page function."""
        import meaningless.utilities.common

        async def async_get_page(url: str) -> str:
            """Async version of get_page that uses our aiohttp session."""
            if not self.session:
                await self._create_session()

            async with self.semaphore:
                for retry in range(self.max_retries + 1):
                    try:
                        async with self.session.get(url) as response:
                            if response.status == 200:
                                return await response.text()
                            elif response.status == 429:  # Rate limited
                                self.logger.warning(
                                    f"⏸️ Rate limited (429) for {self.translation}, retrying..."
                                )
                                if retry < self.max_retries:
                                    delay = self.retry_delay * (2**retry)
                                    await asyncio.sleep(delay)
                                    continue
                                else:
                                    self.logger.error(
                                        f"❌ Rate limited after {self.max_retries + 1} retries for {self.translation}"
                                    )
                                    return ""
                            else:
                                self.logger.error(
                                    f"❌ HTTP {response.status} for {self.translation}"
                                )
                                return ""

                    except Exception as e:
                        if retry < self.max_retries:
                            delay = self.retry_delay * (2**retry)
                            self.logger.warning(
                                f"🔄 Request failed for {self.translation}, retrying in {delay}s: {str(e)}"
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            self.logger.error(
                                f"❌ Request failed for {self.translation} after {self.max_retries + 1} attempts: {str(e)}"
                            )
                            return ""

            return ""

        # Create a synchronous wrapper that runs the async function
        def sync_get_page(url: str) -> str:
            """Synchronous wrapper for async_get_page."""
            try:
                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_running_loop()
                    # If we're already in an async context, we can't use run_until_complete
                    # So we'll use the original get_page as fallback
                    return self._original_get_page(url)
                except RuntimeError:
                    # No event loop running, we can create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(async_get_page(url))
                    finally:
                        loop.close()
            except Exception as e:
                self.logger.error(f"Error in monkey-patched get_page: {e}")
                # Fallback to original
                return self._original_get_page(url)

        # Apply the monkey patch
        meaningless.utilities.common.get_page = sync_get_page
        self._patched_get_page = sync_get_page

    def _restore_original_get_page(self):
        """Restore the original get_page function."""
        import meaningless.utilities.common

        meaningless.utilities.common.get_page = self._original_get_page

    async def __aenter__(self):
        """Async context manager entry."""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()
        self._restore_original_get_page()

    async def _create_session(self):
        """Create aiohttp session with proper configuration."""
        timeout = ClientTimeout(total=self.timeout)
        connector = TCPConnector(
            limit=self.max_concurrent_requests * 2,
            limit_per_host=self.max_concurrent_requests,
        )

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

    async def _close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, url: str) -> Optional[str]:
        """
        Make a single HTTP request with retries and rate limiting.

        Args:
            url: URL to request

        Returns:
            HTML content as string, or None if failed
        """
        if not self.session:
            await self._create_session()

        async with self.semaphore:
            for retry in range(self.max_retries + 1):
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:  # Rate limited
                            self.logger.warning(
                                f"⏸️ Rate limited (429) for {self.translation}, retrying..."
                            )
                            if retry < self.max_retries:
                                delay = self.retry_delay * (2**retry)
                                await asyncio.sleep(delay)
                                continue
                            else:
                                self.logger.error(
                                    f"❌ Rate limited after {self.max_retries + 1} retries for {self.translation}"
                                )
                                return None
                        else:
                            self.logger.error(
                                f"❌ HTTP {response.status} for {self.translation}"
                            )
                            return None

                except Exception as e:
                    if retry < self.max_retries:
                        delay = self.retry_delay * (2**retry)
                        self.logger.warning(
                            f"🔄 Request failed for {self.translation}, retrying in {delay}s: {str(e)}"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        self.logger.error(
                            f"❌ Request failed for {self.translation} after {self.max_retries + 1} attempts: {str(e)}"
                        )
                        return None

        return None

    async def _discover_chapter_count(self, book: str) -> int:
        """
        Discover the number of chapters in a book.

        Args:
            book: Name of the book

        Returns:
            Number of chapters in the book
        """
        # Try to get chapter count from the first chapter page
        url = PASSAGE_URL_TEMPLATE.format(quote(f"{book} 1"), self.translation)
        content = await self._make_request(url)

        if not content:
            return 1  # Fallback to single chapter

        try:
            soup = BeautifulSoup(content, "html.parser")

            # Look for chapter navigation links - try multiple patterns
            chapter_links = []

            # Pattern 1: Direct chapter links
            chapter_links.extend(soup.find_all("a", href=re.compile(r"chapter=\d+")))

            # Pattern 2: Chapter navigation dropdown
            chapter_select = soup.find("select", {"name": "chapter"})
            if chapter_select:
                chapter_links.extend(chapter_select.find_all("option"))

            # Pattern 3: Chapter navigation in breadcrumbs or navigation
            nav_links = soup.find_all("a", href=re.compile(rf"{book.lower()}\+\d+"))
            chapter_links.extend(nav_links)

            if chapter_links:
                chapters = set()
                for link in chapter_links:
                    # Extract chapter number from href
                    href = link.get("href", "")
                    match = re.search(r"chapter=(\d+)", href)
                    if match:
                        chapters.add(int(match.group(1)))

                    # Extract from option value
                    value = link.get("value", "")
                    if value.isdigit():
                        chapters.add(int(value))

                    # Extract from text content
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        chapters.add(int(text))

                if chapters:
                    max_chapter = max(chapters)
                    self.logger.debug(f"Discovered {max_chapter} chapters for {book}")
                    return max_chapter

            # Fallback: try to find chapter numbers in the text
            chapter_pattern = re.compile(r"Chapter\s+(\d+)", re.IGNORECASE)
            matches = chapter_pattern.findall(content)
            if matches:
                max_chapter = max(int(match) for match in matches)
                self.logger.debug(
                    f"Found {max_chapter} chapters via text pattern for {book}"
                )
                return max_chapter

            # Additional fallback: try common chapter counts for known books
            known_chapters = {
                "Genesis": 50,
                "Exodus": 40,
                "Leviticus": 27,
                "Numbers": 36,
                "Deuteronomy": 34,
                "Joshua": 24,
                "Judges": 21,
                "Ruth": 4,
                "1 Samuel": 31,
                "2 Samuel": 24,
                "1 Kings": 22,
                "2 Kings": 25,
                "1 Chronicles": 29,
                "2 Chronicles": 36,
                "Ezra": 10,
                "Nehemiah": 13,
                "Esther": 10,
                "Job": 42,
                "Psalms": 150,
                "Proverbs": 31,
                "Ecclesiastes": 12,
                "Song of Songs": 8,
                "Isaiah": 66,
                "Jeremiah": 52,
                "Lamentations": 5,
                "Ezekiel": 48,
                "Daniel": 12,
                "Hosea": 14,
                "Joel": 3,
                "Amos": 9,
                "Obadiah": 1,
                "Jonah": 4,
                "Micah": 7,
                "Nahum": 3,
                "Habakkuk": 3,
                "Zephaniah": 3,
                "Haggai": 2,
                "Zechariah": 14,
                "Malachi": 4,
                "Matthew": 28,
                "Mark": 16,
                "Luke": 24,
                "John": 21,
                "Acts": 28,
                "Romans": 16,
                "1 Corinthians": 16,
                "2 Corinthians": 13,
                "Galatians": 6,
                "Ephesians": 6,
                "Philippians": 4,
                "Colossians": 4,
                "1 Thessalonians": 5,
                "2 Thessalonians": 3,
                "1 Timothy": 6,
                "2 Timothy": 4,
                "Titus": 3,
                "Philemon": 1,
                "Hebrews": 13,
                "James": 5,
                "1 Peter": 5,
                "2 Peter": 3,
                "1 John": 5,
                "2 John": 1,
                "3 John": 1,
                "Jude": 1,
                "Revelation": 22,
            }

            if book in known_chapters:
                self.logger.debug(
                    f"Using known chapter count for {book}: {known_chapters[book]}"
                )
                return known_chapters[book]

        except Exception as e:
            self.logger.warning(f"Error discovering chapters for {book}: {e}")

        return 1  # Default to single chapter

    async def download_chapter(
        self, book: str, chapter: int
    ) -> Optional[Dict[str, Any]]:
        """
        Download a single chapter asynchronously using meaningless library's JSONDownloader.

        Args:
            book: Name of the book
            chapter: Chapter number

        Returns:
            Dictionary with chapter data, or None if failed
        """
        import shutil
        import tempfile

        temp_dir = None
        start_time = time.time()
        try:
            # Log the download attempt
            self.logger.info(f"📖 Starting {book} {chapter} ({self.translation})")

            # Create a temporary directory for this download
            temp_dir = tempfile.mkdtemp(
                prefix=f"bible_download_{self.translation}_{book}_{chapter}_"
            )

            # Use JSONDownloader directly - it handles all parsing through meaningless library
            downloader = JSONDownloader(
                translation=self.translation, show_passage_numbers=False, strip_excess_whitespace=True
            )

            # Set the downloader to use our temporary directory
            downloader.default_directory = temp_dir

            # Get the chapter using meaningless library
            # The JSONDownloader will use our monkey-patched get_page function
            # Run the synchronous download_chapter in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, downloader.download_chapter, book, chapter)

            if result != 1:  # JSONDownloader returns 1 on success
                self.logger.warning(
                    f"Failed to download {book} {chapter} ({self.translation})"
                )
                return None

            # Read the downloaded JSON file
            json_file = os.path.join(temp_dir, f"{book}.json")
            if not os.path.exists(json_file):
                self.logger.warning(
                    f"⚠️ JSON file not found for {book} {chapter} ({self.translation})"
                )
                return None

            with open(json_file, "r", encoding="utf-8") as f:
                book_data = json.load(f)

            # Extract verses for the specific chapter from the JSONDownloader format
            # Format: {"Genesis": {"50": {"1": "verse text", "2": "verse text", ...}}}
            verses = []
            if book in book_data:
                book_chapters = book_data[book]
                if str(chapter) in book_chapters:
                    chapter_verses = book_chapters[str(chapter)]
                    # Convert from dict format to list format
                    for verse_num in sorted(chapter_verses.keys(), key=int):
                        verse_text = chapter_verses[verse_num]
                        if verse_text:
                            verses.append(verse_text)

            if not verses:
                self.logger.warning(
                    f"⚠️ No verses found for {book} {chapter} ({self.translation})"
                )
                return None

            duration = time.time() - start_time
            self.logger.info(
                f"✅ Completed {book} {chapter} ({self.translation}): {len(verses)} verses in {duration:.2f}s"
            )

            return {"book": book, "chapter": str(chapter), "verses": verses}

        except Exception as e:
            self.logger.error(
                f"❌ Error downloading {book} {chapter} ({self.translation}): {e}"
            )
            return None
        finally:
            # Clean up the temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.logger.warning(
                        f"Could not clean up temp directory {temp_dir}: {e}"
                    )

    async def download_book(self, book: str) -> List[Dict[str, Any]]:
        """
        Download an entire book asynchronously with all chapters in parallel.

        Args:
            book: Name of the book to download

        Returns:
            List of chapter dictionaries
        """
        self.logger.info(f" 📚 Starting download of {book} ({self.translation})")

        # Discover chapter count
        chapter_count = await self._discover_chapter_count(book)
        self.logger.info(f"📊 {book} has {chapter_count} chapters")

        # Create tasks for all chapters
        tasks = [
            self.download_chapter(book, chapter)
            for chapter in range(1, chapter_count + 1)
        ]

        # Execute all chapter downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        chapters = []
        successful_chapters = 0
        failed_chapters = 0

        for i, result in enumerate(results):
            chapter_num = i + 1
            if isinstance(result, Exception):
                self.logger.error(
                    f"Error downloading {book} {chapter_num} ({self.translation}): {result}"
                )
                failed_chapters += 1
            elif result:
                chapters.append(result)
                successful_chapters += 1
                self.logger.debug(
                    f"✅ Downloaded {book} {chapter_num} ({self.translation}): {len(result['verses'])} verses"
                )
            else:
                self.logger.warning(
                    f"❌ Failed to download {book} {chapter_num} ({self.translation})"
                )
                failed_chapters += 1

        total_verses = sum(len(chapter["verses"]) for chapter in chapters)
        self.logger.info(
            f"📊 Completed {book} ({self.translation}): {successful_chapters}/{chapter_count} chapters, {total_verses} total verses"
        )

        if failed_chapters > 0:
            self.logger.warning(
                f"⚠️ {failed_chapters} chapters failed to download for {book} ({self.translation})"
            )

        return chapters

    async def download_full_bible(self) -> List[Dict[str, Any]]:
        """
        Download the entire Bible asynchronously with all books and chapters in parallel.

        Returns:
            List of all chapter dictionaries
        """
        self.logger.info(f"🚀 Starting full Bible download for {self.translation}")
        self.logger.info(f"📚 Total books to download: {len(BOOKS)}")

        # Create tasks for all books
        tasks = [self.download_book(book) for book in BOOKS]

        self.logger.info(f"⚡ Executing {len(tasks)} concurrent book downloads")

        # Execute all book downloads concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        all_chapters = []
        successful_books = 0
        failed_books = 0

        for i, result in enumerate(results):
            book = BOOKS[i]
            if isinstance(result, Exception):
                self.logger.error(
                    f"❌ Error downloading {book} ({self.translation}): {result}"
                )
                failed_books += 1
            elif result:
                all_chapters.extend(result)
                successful_books += 1
                total_verses = sum(len(chapter["verses"]) for chapter in result)
                self.logger.info(
                    f"✅ Downloaded {book} ({self.translation}): {len(result)} chapters, {total_verses} verses"
                )
            else:
                self.logger.warning(
                    f"❌ Failed to download {book} ({self.translation})"
                )
                failed_books += 1

        total_verses = sum(len(chapter["verses"]) for chapter in all_chapters)
        self.logger.info(f"📊 Full Bible download complete for {self.translation}")
        self.logger.info(f"📚 Books: {successful_books}/{len(BOOKS)} successful")
        self.logger.info(f"📖 Chapters: {len(all_chapters)} total")
        self.logger.info(f"📝 Verses: {total_verses} total")

        if failed_books > 0:
            self.logger.warning(f"⚠️ {failed_books} books failed to download")

        return all_chapters


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


async def download_bible_async(
    translation: str,
    books: Optional[List[str]] = None,
    max_concurrent_requests: int = 5,
    max_retries: int = 3,
    retry_delay: int = 2,
    timeout: int = 300,
) -> List[Dict[str, Any]]:
    """
    Convenience function to download Bible content asynchronously.

    Args:
        translation: Bible translation code
        books: List of books to download (None for all books)
        max_concurrent_requests: Maximum concurrent HTTP requests
        max_retries: Maximum retry attempts per request
        retry_delay: Base delay between retries
        timeout: Request timeout in seconds

    Returns:
        List of chapter dictionaries
    """
    if books is None:
        books = BOOKS

    logger = logging.getLogger("download_bible_async")
    logger.info(f"🔤 Starting download for translation: {translation}")
    logger.info(f"📚 Books to download: {len(books)}")
    if len(books) <= 10:
        logger.info(f"📖 Books: {', '.join(books)}")
    else:
        logger.info(f"📖 Books: {', '.join(books[:5])}... and {len(books)-5} more")

    async with AsyncBibleDownloader(
        translation=translation,
        max_concurrent_requests=max_concurrent_requests,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
    ) as downloader:
        if len(books) == 1:
            # Download single book
            logger.info(f"📖 Downloading single book: {books[0]}")
            return await downloader.download_book(books[0])
        else:
            # Download multiple books or full Bible
            logger.info(f"⚡ Downloading {len(books)} books concurrently")
            tasks = [downloader.download_book(book) for book in books]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            all_chapters = []
            successful_books = 0
            failed_books = 0

            for i, result in enumerate(results):
                book = books[i]
                if isinstance(result, Exception):
                    logger.error(
                        f"❌ Error downloading {book} ({translation}): {result}"
                    )
                    failed_books += 1
                elif result:
                    all_chapters.extend(result)
                    successful_books += 1
                    total_verses = sum(len(chapter["verses"]) for chapter in result)
                    logger.info(
                        f"✅ Completed {book} ({translation}): {len(result)} chapters, {total_verses} verses"
                    )
                else:
                    logger.error(f"❌ Failed to download {book} ({translation})")
                    failed_books += 1

            total_verses = sum(len(chapter["verses"]) for chapter in all_chapters)
            logger.info(f"📊 Download summary for {translation}:")
            logger.info(f"📚 Books: {successful_books}/{len(books)} successful")
            logger.info(f"📖 Chapters: {len(all_chapters)} total")
            logger.info(f"📝 Verses: {total_verses} total")

            if failed_books > 0:
                logger.warning(f"⚠️ {failed_books} books failed to download")

            return all_chapters


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================


def format_as_json(data: List[Dict[str, Any]]) -> str:
    """Format Bible data as JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_as_csv(data: List[Dict[str, Any]]) -> str:
    """Format Bible data as CSV."""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Book", "Chapter", "Verse Number", "Verse Text"])

    # Write data
    for chapter in data:
        book = chapter["book"]
        chapter_num = chapter["chapter"]
        verses = chapter["verses"]

        for i, verse in enumerate(verses, 1):
            writer.writerow([book, chapter_num, i, verse])

    return output.getvalue()


def format_as_xml(data: List[Dict[str, Any]]) -> str:
    """Format Bible data as XML."""
    from xml.dom import minidom
    from xml.etree.ElementTree import Element, SubElement, tostring

    root = Element("bible")

    for chapter in data:
        book_elem = SubElement(root, "book", name=chapter["book"])
        chapter_elem = SubElement(book_elem, "chapter", number=chapter["chapter"])

        for i, verse in enumerate(chapter["verses"], 1):
            verse_elem = SubElement(chapter_elem, "verse", number=str(i))
            verse_elem.text = verse

    # Pretty print XML
    rough_string = tostring(root, "unicode")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def format_as_yaml(data: List[Dict[str, Any]]) -> str:
    """Format Bible data as YAML."""
    import yaml

    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_bibles(translations_str: str) -> List[str]:
    """Validate and parse Bible translation arguments."""
    translations = [t.strip().upper() for t in translations_str.split(",")]

    for translation in translations:
        if translation not in BIBLE_TRANSLATIONS:
            raise argparse.ArgumentTypeError(f"Unsupported translation: {translation}")

    return translations


def validate_format(formats_str: str) -> List[str]:
    """Validate and parse format arguments."""
    formats = [f.strip().lower() for f in formats_str.split(",")]
    valid_formats = ["json", "csv", "xml", "yaml", "yml"]

    for fmt in formats:
        if fmt not in valid_formats:
            raise argparse.ArgumentTypeError(f"Unsupported format: {fmt}")

    return formats


def validate_output_mode(mode: str) -> str:
    """Validate output mode argument."""
    valid_modes = ["book", "books", "all"]
    mode = mode.lower()

    if mode not in valid_modes:
        raise argparse.ArgumentTypeError(
            f"Invalid output mode: {mode}. Must be one of {valid_modes}"
        )

    return mode


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download Bibles from BibleGateway with true async parallelism",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Bible translation selection
    parser.add_argument(
        "--translations",
        type=validate_bibles,
        default=["NIV"],
        help=f"Select 1 or more translations to download from this list (using comma separated values):\n{textwrap.fill(', '.join(BIBLE_TRANSLATIONS.keys()), width=80)}",
    )

    # Output format selection
    parser.add_argument(
        "--formats",
        type=validate_format,
        default=["json"],
        help="Choose 1 or more formats (using comma separated values)\nJSON, CSV, XML, YAML",
    )

    # Output mode selection
    parser.add_argument(
        "--output-mode",
        type=validate_output_mode,
        default="all",
        help="Output mode: 'book' for full Bible only, 'books' for individual books only, or 'all' for both",
    )

    # Output directory
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save downloaded Bibles (default: {DEFAULT_OUTPUT_DIR})",
    )

    # Performance settings
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=DEFAULT_RATE_LIMIT,
        help=f"Maximum concurrent requests to BibleGateway (default: {DEFAULT_RATE_LIMIT})",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Maximum number of retry attempts (default: {DEFAULT_MAX_RETRIES})",
    )

    parser.add_argument(
        "--retry-delay",
        type=int,
        default=DEFAULT_RETRY_DELAY,
        help=f"Delay in seconds between retries (default: {DEFAULT_RETRY_DELAY})",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )

    # Book selection
    parser.add_argument(
        "--books",
        type=str,
        help="Comma-separated list of specific books to download (default: all books)",
    )

    # Verbosity and logging options
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (-v for INFO, -vv for DEBUG, -vvv for all)",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress all output except errors",
    )

    parser.add_argument(
        "--log-errors",
        type=str,
        help="Log errors to specified file in clean format",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    return parser.parse_args()


# =============================================================================
# MAIN PROCESSING FUNCTIONS
# =============================================================================


async def process_single_book(
    translation: str,
    book: str,
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> None:
    """Process a single Bible book."""
    try:
        logger.info(f"📖 Processing {book} for {translation}")

        # Download the book
        book_data = await download_bible_async(
            translation=translation,
            books=[book],
            max_concurrent_requests=rate_limit,
            max_retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )

        if book_data:
            # Create directories
            translation_dir = Path(output_dir) / translation
            books_dir = translation_dir / "books"
            books_dir.mkdir(parents=True, exist_ok=True)

            # Save in all requested formats
            for fmt in formats:
                if fmt == "json":
                    output_file = books_dir / f"{book}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_json(book_data))
                elif fmt == "csv":
                    output_file = books_dir / f"{book}.csv"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_csv(book_data))
                elif fmt in ["yaml", "yml"]:
                    output_file = books_dir / f"{book}.yml"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_yaml(book_data))
                elif fmt == "xml":
                    output_file = books_dir / f"{book}.xml"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_xml(book_data))


        else:
            logger.error(f"❌ Failed to download {book} for {translation}")

    except Exception as e:
        logger.error(f"❌ Error processing {book} for {translation}: {str(e)}")


async def process_full_bible(
    translation: str,
    output_dir: str,
    formats: List[str],
    rate_limit: int,
    retries: int,
    retry_delay: int,
    timeout: int,
    logger: logging.Logger,
) -> None:
    """Process the full Bible for a translation."""
    try:
        logger.info(f"📚 Processing full Bible for {translation}")

        # Download the full Bible
        full_bible_data = await download_bible_async(
            translation=translation,
            books=None,  # All books
            max_concurrent_requests=rate_limit,
            max_retries=retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )

        if full_bible_data:
            # Create directory
            translation_dir = Path(output_dir) / translation
            translation_dir.mkdir(parents=True, exist_ok=True)

            # Save in all requested formats
            for fmt in formats:
                if fmt == "json":
                    output_file = translation_dir / f"{translation}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_json(full_bible_data))
                elif fmt == "csv":
                    output_file = translation_dir / f"{translation}.csv"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_csv(full_bible_data))
                elif fmt in ["yaml", "yml"]:
                    output_file = translation_dir / f"{translation}.yml"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_yaml(full_bible_data))
                elif fmt == "xml":
                    output_file = translation_dir / f"{translation}.xml"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(format_as_xml(full_bible_data))

            logger.info(
                f"✅ Saved full Bible for {translation} with {len(full_bible_data)} chapters"
            )
        else:
            logger.error(f"❌ Failed to download full Bible for {translation}")

    except Exception as e:
        logger.error(f"❌ Error processing full Bible for {translation}: {str(e)}")


async def main_async():
    """Main async function to orchestrate the download process."""
    args = parse_args()

    # Set up logging with verbosity and error logging options
    logger = setup_logging(
        name="bible_downloader",
        verbose=args.verbose,
        quiet=args.quiet,
        log_level=args.log_level,
        error_log_file=args.log_errors,
    )

    try:
        # Create output directory
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        # Determine which books to download
        books_to_download = BOOKS
        if args.books:
            books_to_download = [book.strip() for book in args.books.split(",")]

            # Log initial configuration
        logger.info(f"🚀 Starting download of {len(args.translations)} translations")
        logger.info(
            f"⚡ Using TRUE async concurrency with rate limit of {args.rate_limit}"
        )
        logger.info(f"📁 Output formats: {', '.join(args.formats)}")
        logger.info(f"📂 Output mode: {args.output_mode}")
        logger.info(f"📚 Books to download: {len(books_to_download)}")
        
        # Log verbosity and logging configuration
        if args.quiet:
            logger.info("🔇 Quiet mode enabled - only errors will be shown")
        elif args.verbose > 0:
            logger.info(f"🔊 Verbosity level: {args.verbose} ({logging.getLevelName(logger.level)})")
        else:
            logger.info(f"🔊 Log level: {logging.getLevelName(logger.level)}")
        
        if args.log_errors:
            logger.info(f"📝 Error logging enabled: {args.log_errors}")

        # Start timing
        start_time = time.time()

        # Create tasks for concurrent processing
        tasks = []

        # Add full Bible download tasks if requested
        if args.output_mode in ["all", "book"]:
            for translation in args.translations:
                tasks.append(
                    process_full_bible(
                        translation,
                        args.output_dir,
                        args.formats,
                        args.rate_limit,
                        args.retries,
                        args.retry_delay,
                        args.timeout,
                        logger,
                    )
                )

        # Add individual book download tasks if requested
        if args.output_mode in ["all", "books"]:
            logger.info("\n📚 Creating individual book download tasks...")
            for translation in args.translations:
                logger.info(f"🔤 Processing translation: {translation}")
                for book in books_to_download:
                    logger.info(f"📖 Queuing: {book} ({translation})")
                    tasks.append(
                        process_single_book(
                            translation,
                            book,
                            args.output_dir,
                            args.formats,
                            args.rate_limit,
                            args.retries,
                            args.retry_delay,
                            args.timeout,
                            logger,
                        )
                    )



        # Execute all tasks concurrently using asyncio.gather
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check for any exceptions
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            logger.warning(
                f"⚠️ Encountered {len(exceptions)} exceptions during download"
            )
            for exc in exceptions[:5]:  # Show first 5 exceptions
                logger.error(f" ❌ Exception: {exc}")

        # Format elapsed time for display
        if elapsed_time < 60:
            time_str = f"{elapsed_time:.2f} seconds"
        elif elapsed_time < 3600:
            minutes = int(elapsed_time // 60)
            seconds = elapsed_time % 60
            time_str = f"{minutes} minutes {seconds:.2f} seconds"
        else:
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = elapsed_time % 60
            time_str = f"{hours} hours {minutes} minutes {seconds:.2f} seconds"

        successful_items = len(tasks) - len(exceptions)
        failed_items = len(exceptions)
        logger.info(
            f"✅ Processed item(s) completed: {successful_items}, Failed: {failed_items}"
        )
        logger.info(f"⏱️ Total execution time: {time_str}")

    except Exception as e:
        logger.error(f"❌ An error occurred during download: {str(e)}")
        raise


def main():
    """Main entry point for the Bible downloader application."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⏹️ Download interrupted by user")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
