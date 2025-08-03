#!/usr/bin/env python3

import argparse
import asyncio
import json
import logging
import multiprocessing
import os
import shutil
import tempfile
import textwrap
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from meaningless import JSONDownloader
from meaningless.utilities.common import BIBLE_TRANSLATIONS

from utils.formatting import (
    format_as_csv,
    format_as_xml,
    format_as_yaml,
)
from utils.logging import setup_logging
from utils.validation import validate_bibles, validate_format, validate_output_mode

# Static configuration for concurrency
NUM_PROCESSES = multiprocessing.cpu_count()  # Use all available CPU cores
THREADS_PER_PROCESS = 10  # Number of concurrent downloads per process
MAX_RETRIES = 3  # Maximum number of retry attempts for failed downloads
RETRY_DELAY = 2  # Delay in seconds between retry attempts
RATE_LIMIT = 5  # Maximum number of concurrent requests to BibleGateway
RATE_LIMIT_DELAY = 1  # Delay in seconds between requests
DEFAULT_OUTPUT_DIR = os.path.join(
    os.getcwd(), "bibles"
)  # Default output directory in current working directory

# Create a semaphore for rate limiting
rate_limiter = asyncio.Semaphore(RATE_LIMIT)

logger = logging.getLogger("colored")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()

# Only Supported version available for download
TRANSLATIONS = [
    "AMP",
    "ASV",
    "AKJV",
    "BRG",
    "CSB",
    "EHV",
    "ESV",
    "ESVUK",
    "GNV",
    "GW",
    "ISV",
    "JUB",
    "KJV",
    "KJ21",
    "LEB",
    "LSB",
    "MEV",
    "NASB",
    "NASB1995",
    "NET",
    "NIV",
    "NIVUK",
    "NKJV",
    "NLT",
    "NLV",
    "NOG",
    "NRSV",
    "NRSVUE",
    "RSV",
    "WEB",
    "YLT",
]

# List of all 66 Bible books in order
BOOKS = [
    # Old Testament
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
    # New Testament
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


def parse_args():
    parser = argparse.ArgumentParser(
        "Download Bibles from BibleGateway",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    wrapped_choices = textwrap.fill(", ".join(TRANSLATIONS), width=80)
    parser.add_argument(
        "--translations",
        type=validate_bibles,
        default=TRANSLATIONS,
        help=f"Select 1 or more translations to download from this list (using comma separated values):\n{wrapped_choices}",
    )
    parser.add_argument(
        "--formats",
        type=validate_format,
        default=["json"],
        help="Choose 1 or more formats (using comma separated values)\nJSON, CSV, YML, XML",
    )
    parser.add_argument(
        "--output-mode",
        type=validate_output_mode,
        default=["all"],
        help="Output mode: 'book' for full book in a single file only, 'books' for individual book files only, or 'all' for both individual book files and full book in a single file (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save downloaded Bibles (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=NUM_PROCESSES,
        help=f"Number of processes to use (default: {NUM_PROCESSES})",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=THREADS_PER_PROCESS,
        help=f"Number of threads per process (default: {THREADS_PER_PROCESS})",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=MAX_RETRIES,
        help=f"Maximum number of retry attempts (default: {MAX_RETRIES})",
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=RETRY_DELAY,
        help=f"Delay in seconds between retries (default: {RETRY_DELAY})",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=RATE_LIMIT,
        help=f"Maximum concurrent requests to BibleGateway (default: {RATE_LIMIT})",
    )
    parser.add_argument(
        "--rate-delay",
        type=int,
        default=RATE_LIMIT_DELAY,
        help=f"Delay in seconds between requests (default: {RATE_LIMIT_DELAY})",
    )
    parser.add_argument(
        "--auto-retry",
        action="store_true",
        help="Automatically retry failed downloads without prompting",
    )
    parser.add_argument(
        "--failed-retries",
        type=int,
        default=3,
        help="Number of times to retry failed downloads (default: 3)",
    )
    return parser.parse_args()


async def download_book(
    downloader: JSONDownloader, book: str, logger: logging.Logger
) -> List[Dict]:
    """
    Download a book from BibleGateway using JSONDownloader.

    :param downloader: JSONDownloader instance
    :type downloader: JSONDownloader
    :param book: Name of the book
    :type book: str
    :param logger: Logger instance
    :type logger: logging.Logger
    :return: List of chapter dictionaries with book, chapter, and verses
    :rtype: List[Dict]
    """
    try:
        logger.info(f"  Downloading {book}")
        # Use the JSONDownloader to download the book to a file
        result = await asyncio.get_event_loop().run_in_executor(
            None, downloader.download_book, book
        )

        if result != 1:  # JSONDownloader returns 1 on success
            logger.error(f"    Download failed for {book}, result: {result}")
            return []

        # Read the downloaded JSON file
        json_file = os.path.join(downloader.default_directory, f"{book}.json")
        if not os.path.exists(json_file):
            logger.error(f"    JSON file not found for {book}: {json_file}")
            return []

        with open(json_file, "r", encoding="utf-8") as f:
            book_data = json.load(f)

        # Convert from JSONDownloader format to our expected format
        converted_data = []
        if book in book_data:
            book_content = book_data[book]
            for chapter_num, chapter_content in book_content.items():
                verses = []
                for verse_num in sorted(chapter_content.keys(), key=int):
                    verse_text = chapter_content[verse_num].strip()
                    # Remove verse numbers if present (like "¹ ", "² ", etc.)
                    if verse_text and verse_text[0].isdigit():
                        # Find the first non-digit character
                        i = 0
                        while i < len(verse_text) and (
                            verse_text[i].isdigit() or verse_text[i] in "⁰¹²³⁴⁵⁶⁷⁸⁹"
                        ):
                            i += 1
                        verse_text = verse_text[i:].strip()
                    verses.append(verse_text)

                converted_data.append(
                    {"book": book, "chapter": chapter_num, "verses": verses}
                )

        logger.info(
            f"    Successfully downloaded {book}: {len(converted_data)} chapters"
        )
        return converted_data

    except Exception as e:
        logger.error(f"    Error downloading {book}: {str(e)}")
        return []


async def download_full_bible(
    downloader: JSONDownloader, logger: logging.Logger
) -> List[Dict]:
    """
    Download the entire Bible from BibleGateway using JSONDownloader.

    :param downloader: JSONDownloader instance
    :type downloader: JSONDownloader
    :param logger: Logger instance
    :type logger: logging.Logger
    :return: List of chapter dictionaries with book, chapter, and verses
    :rtype: List[Dict]
    """
    try:
        logger.info("Downloading full Bible")
        # Use the JSONDownloader to get the full Bible data
        bible_data = await asyncio.get_event_loop().run_in_executor(
            None, downloader.download_book
        )

        if not bible_data:
            logger.error(" No data received for full Bible")
            return []

        logger.info(" Successfully downloaded full Bible")
        return bible_data

    except Exception as e:
        logger.error(f"    Error downloading full Bible: {str(e)}")
        return []


async def process_translation(
    translation,
    output_dir,
    formats,
    failed_downloads_list,
    rate_limit,
    rate_delay,
    max_retries,
    retry_delay,
    output_mode="all",
    temp_dir=None,
):
    # Get the full translation name from BIBLE_TRANSLATIONS
    full_translation = next(
        (k for k, v in BIBLE_TRANSLATIONS.items() if k.upper() == translation.upper()),
        translation,
    )
    local_translation = translation
    logger = setup_logging("download")
    logger.debug(f"Processing translation: {full_translation}")

    # Create JSONDownloader instance
    downloader = JSONDownloader(
        translation=local_translation, strip_excess_whitespace=True
    )

    # Set the downloader to use the temp directory
    downloader.default_directory = output_dir

    # Create translation output directory
    translation_dir = os.path.join(output_dir, full_translation)
    os.makedirs(translation_dir, exist_ok=True)

    # Download all books for full Bible if needed
    full_bible_data = []
    if output_mode in ["all", "book"]:
        logger.info("Downloading all books for full Bible output")
        # Download all books concurrently
        tasks = [download_book(downloader, book, logger) for book in BOOKS]
        results = await asyncio.gather(*tasks)

        # Debug: Check what we got back
        logger.info(f"  Downloaded {len(results)} books, checking results...")
        for i, (book, result) in enumerate(zip(BOOKS, results)):
            logger.info(f"    {book}: {len(result) if result else 0} chapters")

        # Flatten the list of lists (each book is a list of chapters)
        for book_result in results:
            if book_result:
                full_bible_data.extend(book_result)

        logger.info(f"  Total chapters in full Bible: {len(full_bible_data)}")

        if full_bible_data:
            logger.info("  Writing full Bible files...")
            # Save full Bible in each requested format
            for fmt in formats:
                if fmt == "json":
                    output_file = os.path.join(
                        translation_dir, f"{full_translation}.json"
                    )
                    logger.info(f"    Writing JSON to {output_file}")
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(full_bible_data, f, indent=2, ensure_ascii=False)
                elif fmt == "csv":
                    output_file = os.path.join(
                        translation_dir, f"{full_translation}.csv"
                    )
                    logger.info(f"    Writing CSV to {output_file}")
                    csv_data = format_as_csv(full_bible_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(csv_data)
                elif fmt == "yml":
                    output_file = os.path.join(
                        translation_dir, f"{full_translation}.yml"
                    )
                    logger.info(f"    Writing YAML to {output_file}")
                    yaml_data = format_as_yaml(full_bible_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(yaml_data)
                elif fmt == "xml":
                    output_file = os.path.join(
                        translation_dir, f"{full_translation}.xml"
                    )
                    logger.info(f"    Writing XML to {output_file}")
                    xml_data = format_as_xml(full_bible_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(xml_data)
                logger.info(f"Saved full Bible as {fmt.upper()}")
        else:
            logger.warning("No data received for full Bible")

    # Download individual books if needed
    if output_mode in ["all", "books"]:
        # Create books directory
        books_dir = os.path.join(translation_dir, "books")
        os.makedirs(books_dir, exist_ok=True)

        # Create tasks for all books
        tasks = [download_book(downloader, book, logger) for book in BOOKS]

        # Wait for all downloads to complete
        results = await asyncio.gather(*tasks)

        # Debug: Check what we got back for individual books
        logger.info(
            f"  Downloaded {len(results)} individual books, checking results..."
        )
        for i, (book, result) in enumerate(zip(BOOKS, results)):
            logger.info(f"    {book}: {len(result) if result else 0} chapters")

        # Filter out failed downloads
        successful_books = [(book, data) for book, data in zip(BOOKS, results) if data]
        failed_books = [book for book, data in zip(BOOKS, results) if not data]

        logger.info(
            f"  Successful books: {len(successful_books)}, Failed books: {len(failed_books)}"
        )

        if failed_books:
            logger.warning(
                f"Failed to download {len(failed_books)} books for {full_translation}: {', '.join(failed_books)}"
            )
            # Add failed books to the failed_downloads_list
            for book in failed_books:
                failed_downloads_list.append(
                    {"translation": local_translation, "book": book, "formats": formats}
                )

        # Save individual books in each requested format
        for book, book_data in successful_books:
            logger.info(f"    Writing individual book: {book}")
            for fmt in formats:
                if fmt == "json":
                    output_file = os.path.join(books_dir, f"{book}.json")
                    logger.info(f"      Writing {book}.json")
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(book_data, f, indent=2, ensure_ascii=False)
                elif fmt == "csv":
                    output_file = os.path.join(books_dir, f"{book}.csv")
                    logger.info(f"      Writing {book}.csv")
                    csv_data = format_as_csv(book_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(csv_data)
                elif fmt == "yml":
                    output_file = os.path.join(books_dir, f"{book}.yml")
                    logger.info(f"      Writing {book}.yml")
                    yaml_data = format_as_yaml(book_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(yaml_data)
                elif fmt == "xml":
                    output_file = os.path.join(books_dir, f"{book}.xml")
                    logger.info(f"      Writing {book}.xml")
                    xml_data = format_as_xml(book_data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(xml_data)
            logger.info(f"    Saved {book} in all formats")

    logger.info(f"Completed processing {full_translation}")


def process_translations_chunk(
    translations_chunk,
    output_dir,
    formats,
    failed_downloads_list,
    rate_limit,
    rate_delay,
    max_retries,
    retry_delay,
    output_mode="all",
    temp_dir=None,
):
    # Set up the event loop for this process
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Create tasks for all translations in this chunk
        tasks = [
            process_translation(
                translation,
                output_dir,
                formats,
                failed_downloads_list,
                rate_limit,
                rate_delay,
                max_retries,
                retry_delay,
                output_mode,
                temp_dir,
            )
            for translation in translations_chunk
        ]

        # Wait for all tasks to complete
        loop.run_until_complete(asyncio.gather(*tasks))

    finally:
        loop.close()


async def retry_failed_downloads(
    failed_downloads_list,
    output_dir,
    formats,
    rate_limit,
    rate_delay,
    max_retries,
    retry_delay,
    auto_retry=False,
    max_failed_retries=3,
    temp_dir=None,
):
    """
    Retry failed downloads with exponential backoff.

    :param failed_downloads_list: List of failed downloads to retry
    :type failed_downloads_list: List[Dict]
    :param output_dir: Output directory for downloads
    :type output_dir: str
    :param formats: List of output formats
    :type formats: List[str]
    :param rate_limit: Rate limit for concurrent requests
    :type rate_limit: int
    :param rate_delay: Delay between requests
    :type rate_delay: int
    :param max_retries: Maximum number of retries
    :type max_retries: int
    :param retry_delay: Delay between retries
    :type retry_delay: int
    :param auto_retry: Whether to automatically retry without prompting
    :type auto_retry: bool
    :param max_failed_retries: Maximum number of times to retry failed downloads
    :type max_failed_retries: int
    :param temp_dir: Temporary directory path
    :type temp_dir: str
    """
    if not failed_downloads_list:
        return

    logger = setup_logging("download")
    logger.warning(f"Retrying {len(failed_downloads_list)} failed downloads")

    if not auto_retry:
        response = input("Do you want to retry failed downloads? (y/n): ")
        if response.lower() != "y":
            logger.info("Skipping retry of failed downloads")
            return

    retry_count = 0
    while failed_downloads_list and retry_count < max_failed_retries:
        retry_count += 1
        logger.info(f"Retry attempt {retry_count} for failed downloads")

        # Create a copy of the failed downloads list for this retry
        current_failed = failed_downloads_list.copy()
        failed_downloads_list.clear()

        # Process each failed download
        for failed_download in current_failed:
            translation = failed_download["translation"]
            book = failed_download["book"]
            formats = failed_download["formats"]

            try:
                # Create JSONDownloader instance
                downloader = JSONDownloader(
                    translation=translation, strip_excess_whitespace=True
                )
                # Try to download the book again
                book_data = await asyncio.get_event_loop().run_in_executor(
                    None, downloader.download_book, book
                )

                if book_data:
                    # Save the book in each requested format
                    translation_dir = os.path.join(output_dir, translation)
                    books_dir = os.path.join(translation_dir, "books")
                    os.makedirs(books_dir, exist_ok=True)

                    for fmt in formats:
                        if fmt == "json":
                            output_file = os.path.join(books_dir, f"{book}.json")
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(book_data, f, indent=2, ensure_ascii=False)
                        elif fmt == "csv":
                            output_file = os.path.join(books_dir, f"{book}.csv")
                            csv_data = format_as_csv(book_data)
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(csv_data)
                        elif fmt == "yml":
                            output_file = os.path.join(books_dir, f"{book}.yml")
                            yaml_data = format_as_yaml(book_data)
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(yaml_data)
                        elif fmt == "xml":
                            output_file = os.path.join(books_dir, f"{book}.xml")
                            xml_data = format_as_xml(book_data)
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(xml_data)

                    logger.info(
                        f"Successfully retried download of {book} for {translation}"
                    )
                else:
                    # Add back to failed downloads list for next retry
                    failed_downloads_list.append(failed_download)

            except Exception as e:
                logger.error(f"Error retrying {book} for {translation}: {str(e)}")
                # Add back to failed downloads list for next retry
                failed_downloads_list.append(failed_download)

        # Wait before next retry
        if failed_downloads_list and retry_count < max_failed_retries:
            wait_time = retry_delay * (2 ** (retry_count - 1))  # Exponential backoff
            logger.info(f"Waiting {wait_time} seconds before next retry")
            await asyncio.sleep(wait_time)

    if failed_downloads_list:
        logger.error(
            f"Failed to download {len(failed_downloads_list)} items after {max_failed_retries} retries"
        )
        for failed_download in failed_downloads_list:
            logger.error(
                f"  - {failed_download['book']} for {failed_download['translation']}"
            )


async def main_async():
    """Main async function to orchestrate the download process."""
    args = parse_args()

    # Set up logging
    logger = setup_logging("download")

    # Always use a system temp directory for downloads
    temp_dir = tempfile.mkdtemp(prefix="bible_download_")
    original_output_dir = args.output_dir

    try:
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Initialize failed downloads list
        failed_downloads_list = []

        # Calculate chunk size for multiprocessing
        chunk_size = max(1, len(args.translations) // args.processes)

        # Split translations into chunks
        translation_chunks = [
            args.translations[i : i + chunk_size]
            for i in range(0, len(args.translations), chunk_size)
        ]

        logger.info(f"Starting download of {len(args.translations)} translations")
        logger.info(
            f"Using {args.processes} processes with {args.threads} threads each"
        )
        logger.info(f"Output formats: {', '.join(args.formats)}")
        logger.info(f"Output mode: {args.output_mode}")

        # Process translations in parallel
        with ThreadPoolExecutor(max_workers=args.processes) as executor:
            futures = [
                executor.submit(
                    process_translations_chunk,
                    chunk,
                    temp_dir,  # Use temp_dir for all downloads
                    args.formats,
                    failed_downloads_list,
                    args.rate_limit,
                    args.rate_delay,
                    args.retries,
                    args.retry_delay,
                    args.output_mode,
                )
                for chunk in translation_chunks
            ]

            # Wait for all futures to complete
            for future in futures:
                future.result()

        # Retry failed downloads if any
        if failed_downloads_list:
            await retry_failed_downloads(
                failed_downloads_list,
                temp_dir,
                args.formats,
                args.rate_limit,
                args.rate_delay,
                args.retries,
                args.retry_delay,
                args.auto_retry,
                args.failed_retries,
            )

        # Move files from temp directory to final location
        if os.path.exists(original_output_dir):
            shutil.rmtree(original_output_dir)
        shutil.move(temp_dir, original_output_dir)

        logger.info("Download process completed successfully!")

    except Exception as e:
        logger.error(f"An error occurred during download: {str(e)}")
        raise
    finally:
        # Clean up temporary directory if it still exists
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info("Cleaned up temporary directory")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory: {str(e)}")


def main():
    """Main function to run the async download process."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
