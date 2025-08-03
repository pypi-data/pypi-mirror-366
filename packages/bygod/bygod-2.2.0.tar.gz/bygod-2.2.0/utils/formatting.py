#!/usr/bin/env python3

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

import yaml


def format_as_json(data):
    """
    Format Bible data as JSON.

    :param data: Bible data to format (list of dicts with book, chapter, verses)
    :type data: list
    :return: Formatted JSON string
    :rtype: str
    """
    # The data is already in the correct format from meaningless library
    if isinstance(data, list):
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps([], indent=2, ensure_ascii=False)


def format_as_csv(data):
    """
    Format Bible data as CSV.

    :param data: Bible data to format (list of dicts with book, chapter, verses)
    :type data: list
    :return: Formatted CSV string
    :rtype: str
    """
    output = []
    # Add header
    output.append("Book,Chapter,Verse,Text")

    # Process the list of chapter dictionaries
    if isinstance(data, list):
        for chapter_data in data:
            book = chapter_data.get("book", "")
            chapter = chapter_data.get("chapter", "")
            verses = chapter_data.get("verses", [])

            for verse_num, verse_text in enumerate(verses, 1):
                # Properly escape the verse text for CSV
                verse_text = str(verse_text).replace('"', '""')  # Escape quotes
                if "," in verse_text or '"' in verse_text or "\n" in verse_text:
                    verse_text = (
                        f'"{verse_text}"'  # Quote if contains special characters
                    )
                output.append(f"{book},{chapter},{verse_num},{verse_text}")

    return "\n".join(output)


def format_as_yaml(data):
    """
    Format Bible data as YAML.

    :param data: Bible data to format (list of dicts with book, chapter, verses)
    :type data: list
    :return: Formatted YAML string
    :rtype: str
    """
    # The data is already in the correct format from meaningless library
    if isinstance(data, list):
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
    else:
        return yaml.dump([], allow_unicode=True, sort_keys=False)


def format_as_xml(data):
    """
    Format Bible data as XML.

    :param data: Bible data to format (list of dicts with book, chapter, verses)
    :type data: list
    :return: Formatted XML string
    :rtype: str
    """
    root = ET.Element("bible")

    # Process the list of chapter dictionaries
    if isinstance(data, list):
        for chapter_data in data:
            book = chapter_data.get("book", "")
            chapter = chapter_data.get("chapter", "")
            verses = chapter_data.get("verses", [])

            # Create book element if it doesn't exist
            book_elem = None
            for existing_book in root.findall("book"):
                if existing_book.get("name") == book:
                    book_elem = existing_book
                    break

            if book_elem is None:
                book_elem = ET.SubElement(root, "book", name=book)

            # Create chapter element
            chapter_elem = ET.SubElement(book_elem, "chapter", number=chapter)

            # Add verses
            for verse_num, verse_text in enumerate(verses, 1):
                verse_elem = ET.SubElement(chapter_elem, "verse", number=str(verse_num))
                verse_elem.text = str(verse_text)

    # Convert to pretty XML with proper encoding
    xml_str = ET.tostring(root, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")
