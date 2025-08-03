#!/usr/bin/env python3

import asyncio
import re
from typing import Dict, List

import constants
from bs4 import BeautifulSoup
from meaningless.bible_web_extractor import WebExtractor
from meaningless.utilities import common
from meaningless.utilities.common import BIBLE_TRANSLATIONS, get_page

from utils.logging import setup_logging

# Get logger instance
logger = setup_logging("chapters")


def get_chapter_list(translation: str, book_name: str) -> List[str]:
    """
    Gets all available chapter numbers for a given book.

    :param translation: Translation code. For example, 'NIV', 'ESV', 'NLT'
    :type translation: str
    :param book_name: Name of the book
    :type book_name: str
    :return: List of numeric strings corresponding to the chapter numbers available in the specified book
    :rtype: list
    """
    # Look up the translation in the dictionary and return an empty array if not found
    version_string = constants.TRANSLATIONS_DICT.get(translation)
    if not version_string:
        return []

    url = f"https://www.biblegateway.com/versions/{version_string}/#booklist"

    # There's a match, so download the page and search it for the requested book
    soup = BeautifulSoup(get_page(url), "html.parser")

    # The spans inside the chapter's td complicate things - remove them
    [span.decompose() for span in soup.find_all("span")]

    # Search for the book_name and return [] if not found
    found_book_td = soup.find("td", class_="book-name", string=re.compile(book_name))
    if not found_book_td:
        return []

    chapter_list = []
    # Move 2 siblings over from the found td to the rightmost td,
    # and loop through the text of each link (chapter number)
    [
        chapter_list.append(chapter_num)
        for chapter_num in found_book_td.next_sibling.next_sibling.stripped_strings
    ]

    return chapter_list


async def process_translation(translation: str) -> Dict[str, List[int]]:
    """
    Process a single translation to get passage counts for all books.

    :param translation: Translation code (e.g., 'NIV', 'ESV')
    :return: Dictionary with book names as keys and lists of passage counts as values
    """
    logger.info(f"Starting processing for translation: {translation}")
    extractor = WebExtractor(
        translation=translation,
        output_as_list=True,
        show_passage_numbers=True,
        strip_excess_whitespace_from_list=True,
    )

    books_chapters_passages_count_dict = {}

    # Process each book
    for book in constants.BOOKS:
        logger.info(f"Processing book: {book} for translation: {translation}")
        # Get total chapters for this book
        total_chapters = common.get_chapter_count(book, translation=translation)

        # Initialize list for this book's chapter counts
        books_chapters_passages_count_dict[book] = []

        # Create tasks for all chapters in this book
        chapter_tasks = []
        for chapter in range(1, total_chapters + 1):
            # Create a coroutine for get_passage_range
            coro = asyncio.get_event_loop().run_in_executor(
                None,
                extractor.get_passage_range,
                book,
                chapter,
                1,
                chapter,
                common.get_end_of_chapter(),
            )
            chapter_tasks.append((chapter, coro))

        # Wait for all chapters to complete
        for chapter, coro in chapter_tasks:
            try:
                passages = await coro
                passage_count = len(passages)
                books_chapters_passages_count_dict[book].append(passage_count)
                logger.debug(
                    f"Chapter {chapter} in {book} ({translation}): {passage_count} passages"
                )
            except Exception as e:
                logger.error(
                    f"Error processing chapter {chapter} in {book} ({translation}): {str(e)}"
                )
                books_chapters_passages_count_dict[book].append(
                    0
                )  # Add 0 for failed chapters

    logger.info(f"Completed processing for translation: {translation}")
    return books_chapters_passages_count_dict


async def get_chapter_passage_counts_by_translations() -> (
    Dict[str, Dict[str, List[int]]]
):
    """
    Gets the total number of passages for each chapter in all books for all supported translations.
    Uses concurrent processing for better performance.

    :return: Dictionary with translations as keys and nested dictionaries of book passage counts as values
    :rtype: dict
    """
    logger.info("Starting passage count processing for all translations")

    # Create tasks for all translations
    translation_tasks = [
        process_translation(translation) for translation in BIBLE_TRANSLATIONS.keys()
    ]

    # Run all translations concurrently
    results = await asyncio.gather(*translation_tasks, return_exceptions=True)

    # Combine results into final dictionary
    translations_dict = {}
    for translation, result in zip(BIBLE_TRANSLATIONS.keys(), results):
        if isinstance(result, Exception):
            logger.error(f"Error processing translation {translation}: {str(result)}")
            translations_dict[translation] = {}
        else:
            translations_dict[translation] = result

    logger.info("Completed passage count processing for all translations")
    return translations_dict


def get_all_translations_passage_counts() -> Dict[str, Dict[str, List[int]]]:
    """
    Gets passage counts for all translations and books.
    This is a synchronous wrapper around the async get_chapter_passage_counts_by_translations function.

    :return: Dictionary with translations as keys and nested dictionaries of book passage counts as values
    :rtype: dict
    Example:
    {
        'NIV': {
            'Genesis': [31, 25, 24, ...],
            'Exodus': [22, 25, 22, ...],
            ...
        },
        'ESV': {
            'Genesis': [31, 25, 24, ...],
            'Exodus': [22, 25, 22, ...],
            ...
        },
        ...
    }
    """
    try:
        logger.info("Starting to fetch passage counts for all translations")
        # Create and run the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                get_chapter_passage_counts_by_translations()
            )
            logger.info("Successfully fetched passage counts for all translations")
            return results
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error fetching passage counts: {str(e)}")
        return {}


# Example usage:
if __name__ == "__main__":
    # Get passage counts for all translations
    passage_counts = get_all_translations_passage_counts()

    # Print results
    for translation, books in passage_counts.items():
        print(f"\nTranslation: {translation}")
        for book, counts in books.items():
            print(f"{book}: {counts}")
