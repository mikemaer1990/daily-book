#!/usr/bin/env python3
"""
Special extractor for "A Calendar of Wisdom" by Leo Tolstoy
This EPUB has a specific structure where days are organized as "Month Day" headers
"""

import json
import re
from datetime import datetime
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def month_to_number(month_name):
    """Convert month name to number."""
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    return months.get(month_name.lower())


def extract_chapters(epub_path):
    """
    Extract all daily entries from A Calendar of Wisdom.
    Returns dict with MM-DD keys and chapter content as values.
    """
    print(f"Opening EPUB file: {epub_path}")

    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"Error reading EPUB file: {e}")
        return {}

    chapters = {}
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    print(f"\nFound {len(items)} document items in EPUB")
    print("Extracting daily entries...\n")

    total_entries = 0

    for item in items:
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')

        # Get all text content
        full_text = soup.get_text()

        # Split by date patterns like "January 1", "February 2", etc.
        # Pattern: Month name followed by day number
        date_pattern = r'\n\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})\s*\n'

        # Find all date matches with their positions
        matches = list(re.finditer(date_pattern, full_text, re.IGNORECASE))

        for i, match in enumerate(matches):
            month_name = match.group(1)
            day = match.group(2).zfill(2)
            month_num = month_to_number(month_name)

            if not month_num:
                continue

            date_key = f"{month_num}-{day}"

            # Extract content from this date until the next date (or end of text)
            start_pos = match.end()
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(full_text)

            entry_text = full_text[start_pos:end_pos].strip()

            # Clean up the text: remove excessive whitespace but preserve paragraphs
            paragraphs = []
            for para in entry_text.split('\n'):
                para = para.strip()
                if para and len(para) > 1:  # Skip single characters or empty lines
                    paragraphs.append(para)

            # Join paragraphs with double newlines
            clean_text = '\n\n'.join(paragraphs)

            if clean_text and len(clean_text) > 10:  # Make sure there's actual content
                chapters[date_key] = clean_text
                total_entries += 1
                print(f"[OK] Extracted {date_key}: {month_name} {day}")

    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"Total daily entries extracted: {total_entries}")

    return chapters


def save_chapters(chapters, output_file='chapters.json'):
    """Save chapters dictionary to JSON file."""
    # Sort by date key
    sorted_chapters = dict(sorted(chapters.items()))

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_chapters, f, indent=2, ensure_ascii=False)

    print(f"\nChapters saved to: {output_file}")

    # Show some statistics
    if chapters:
        dates = sorted(chapters.keys())
        print(f"Date range: {dates[0]} to {dates[-1]}")
        avg_length = sum(len(content) for content in chapters.values()) / len(chapters)
        print(f"Average entry length: {int(avg_length)} characters")

        # Check for missing dates
        missing = []
        for month in range(1, 13):
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
            for day in range(1, days_in_month + 1):
                date_key = f"{month:02d}-{day:02d}"
                if date_key not in chapters:
                    missing.append(date_key)

        if missing:
            print(f"\nWarning: Missing {len(missing)} dates")
            if len(missing) <= 20:
                print(f"Missing dates: {', '.join(missing)}")
        else:
            print("\n[OK] All 366 dates present (including leap year Feb 29)")


def main():
    epub_path = "a calendar of wisdom.epub"

    # Extract chapters
    chapters = extract_chapters(epub_path)

    if not chapters:
        print("\nError: No entries were extracted!")
        return

    # Save to JSON
    save_chapters(chapters)

    print("\n" + "="*60)
    print("Next steps:")
    print("1. Review chapters.json to ensure all dates are present")
    print("2. Test locally: set environment variables and run send_daily_chapter.py")
    print("3. Commit chapters.json to your git repository")
    print("4. Set up GitHub Actions and Brevo secrets")
    print("="*60)


if __name__ == '__main__':
    main()
