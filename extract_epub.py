#!/usr/bin/env python3
"""
EPUB to JSON Extractor for Daily Book Emailer
Extracts daily chapters from an EPUB file and saves them to chapters.json
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def clean_html(html_content):
    """Convert HTML to clean text while preserving paragraph breaks."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text with paragraph breaks preserved
    paragraphs = []
    for p in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = p.get_text().strip()
        if text:
            paragraphs.append(text)

    # If no paragraphs found, try getting all text
    if not paragraphs:
        text = soup.get_text()
        # Split on multiple newlines and clean up
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

    return '\n\n'.join(paragraphs)


def extract_date_from_title(title):
    """
    Attempt to extract a date from chapter title.
    Handles formats like:
    - "January 1", "Jan 1"
    - "1 January", "1 Jan"
    - "Day 1"
    - "1st January", "2nd February", etc.

    Returns MM-DD format string or None if no date found.
    """
    title = title.strip()

    # Month names mapping
    months = {
        'january': '01', 'jan': '01',
        'february': '02', 'feb': '02',
        'march': '03', 'mar': '03',
        'april': '04', 'apr': '04',
        'may': '05',
        'june': '06', 'jun': '06',
        'july': '07', 'jul': '07',
        'august': '08', 'aug': '08',
        'september': '09', 'sep': '09', 'sept': '09',
        'october': '10', 'oct': '10',
        'november': '11', 'nov': '11',
        'december': '12', 'dec': '12'
    }

    # Pattern 1: "January 1" or "Jan 1"
    pattern1 = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2})'
    match = re.search(pattern1, title, re.IGNORECASE)
    if match:
        month = months[match.group(1).lower()]
        day = match.group(2).zfill(2)
        return f"{month}-{day}"

    # Pattern 2: "1 January" or "1st January", "2nd February", etc.
    pattern2 = r'(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)'
    match = re.search(pattern2, title, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month = months[match.group(2).lower()]
        return f"{month}-{day}"

    # Pattern 3: "Day 1" - assumes sequential from Jan 1
    pattern3 = r'day\s+(\d{1,3})'
    match = re.search(pattern3, title, re.IGNORECASE)
    if match:
        day_number = int(match.group(1))
        if 1 <= day_number <= 366:
            # Convert day of year to MM-DD
            try:
                date = datetime(2024, 1, 1).replace(day=1)  # Using leap year 2024
                from datetime import timedelta
                target_date = date + timedelta(days=day_number - 1)
                return target_date.strftime('%m-%d')
            except:
                pass

    return None


def extract_chapters(epub_path):
    """
    Extract all chapters from EPUB file.
    Returns dict with MM-DD keys and chapter content as values.
    """
    print(f"Opening EPUB file: {epub_path}")

    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"Error reading EPUB file: {e}")
        sys.exit(1)

    chapters = {}
    skipped = []
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    print(f"\nFound {len(items)} document items in EPUB")
    print("Extracting chapters...\n")

    for idx, item in enumerate(items, 1):
        # Get chapter title from item
        title = item.get_name()

        # Try to get better title from content
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')

        # Try to find a title in the content
        title_tag = soup.find(['h1', 'h2', 'h3', 'title'])
        if title_tag:
            content_title = title_tag.get_text().strip()
            if content_title:
                title = content_title

        # Try to extract date from title
        date_key = extract_date_from_title(title)

        if date_key:
            # Clean and extract text content
            text_content = clean_html(content)

            if text_content:
                chapters[date_key] = text_content
                print(f"✓ [{idx}/{len(items)}] {date_key}: {title[:50]}...")
            else:
                skipped.append(f"{title} (empty content)")
        else:
            skipped.append(f"{title} (no date found)")

    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"Total chapters extracted: {len(chapters)}")
    print(f"Items skipped: {len(skipped)}")

    if skipped and len(skipped) <= 20:
        print(f"\nSkipped items:")
        for item in skipped[:10]:
            print(f"  - {item}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")

    return chapters


def save_chapters(chapters, output_file='chapters.json'):
    """Save chapters dictionary to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)
    print(f"\nChapters saved to: {output_file}")

    # Show some statistics
    if chapters:
        dates = sorted(chapters.keys())
        print(f"Date range: {dates[0]} to {dates[-1]}")
        avg_length = sum(len(content) for content in chapters.values()) / len(chapters)
        print(f"Average chapter length: {int(avg_length)} characters")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_epub.py <path-to-epub-file>")
        print("\nExample: python extract_epub.py my-daily-book.epub")
        sys.exit(1)

    epub_path = sys.argv[1]

    if not Path(epub_path).exists():
        print(f"Error: File not found: {epub_path}")
        sys.exit(1)

    if not epub_path.lower().endswith('.epub'):
        print("Warning: File does not have .epub extension")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Extract chapters
    chapters = extract_chapters(epub_path)

    if not chapters:
        print("\nError: No chapters were extracted!")
        print("The EPUB file may have an unusual structure.")
        print("You may need to manually create chapters.json or adjust the extraction logic.")
        sys.exit(1)

    # Save to JSON
    save_chapters(chapters)

    print("\n" + "="*60)
    print("Next steps:")
    print("1. Review chapters.json to ensure all dates are present")
    print("2. Add chapters.json to your git repository")
    print("3. Set up GitHub Actions and Brevo secrets")
    print("4. Test send_daily_chapter.py locally")
    print("="*60)


if __name__ == '__main__':
    main()
