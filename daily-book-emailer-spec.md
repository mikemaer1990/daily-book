# Daily Book Emailer - Project Specification

## Overview
A lightweight automation system that extracts daily chapters from an EPUB file (one-time setup) and automatically emails the chapter for today via GitHub Actions.

## Tech Stack
- **Language**: Python 3.x
- **EPUB Parsing**: `ebooklib` and `BeautifulSoup4`
- **Email**: Brevo (formerly Sendinblue) API
- **Automation**: GitHub Actions (scheduled workflow)
- **Data Storage**: JSON file (committed to repo)

## Project Structure
```
daily-book-emailer/
├── extract_epub.py          # One-time script to convert EPUB to JSON
├── send_daily_chapter.py    # Script to email today's chapter
├── chapters.json            # Extracted book content (generated)
├── requirements.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── daily-email.yml  # GitHub Actions workflow
└── README.md               # Setup instructions
```

## Features

### 1. One-Time EPUB Extraction (`extract_epub.py`)
**Purpose**: Run once locally to extract all daily chapters from EPUB into JSON

**Functionality**:
- Accept EPUB file path as command line argument
- Parse EPUB structure to identify daily chapters
- Extract text content for each day
- Handle common date formats (e.g., "January 1", "Day 1", "1st January")
- Save to `chapters.json` with structure:
```json
{
  "01-01": "Content for January 1st...",
  "01-02": "Content for January 2nd...",
  "12-31": "Content for December 31st..."
}
```
- Use MM-DD format as keys for easy date matching
- Strip HTML formatting but preserve paragraph breaks
- Print extraction progress and total chapters found

**Edge Cases**:
- Handle chapters that might not be perfectly labeled by date
- Provide option to manually map chapters to dates if auto-detection fails
- Skip table of contents, preface, or other non-daily content

### 2. Daily Email Script (`send_daily_chapter.py`)
**Purpose**: Run by GitHub Actions to send today's chapter

**Functionality**:
- Read `chapters.json`
- Get today's date and format as MM-DD
- Find matching chapter content
- Send email via Brevo API with:
  - Subject: "Your Daily Reading - [Date]"
  - Body: Today's chapter content (plain text or HTML)
  - Formatted for readability
- Use GitHub Secrets for Brevo API key and recipient
- Log success/failure

**Environment Variables** (GitHub Secrets):
- `BREVO_API_KEY`: Your Brevo API key
- `SENDER_EMAIL`: Verified sender email in Brevo
- `SENDER_NAME`: Sender name (e.g., "Daily Book Reader")
- `RECIPIENT_EMAIL`: Email address to send to

**Error Handling**:
- If today's date not found in JSON, send notification email
- Handle API connection errors gracefully
- Log all activity with API response codes

### 3. GitHub Actions Workflow (`daily-email.yml`)
**Schedule**: Run daily at 8:00 AM UTC (adjust timezone as needed)

**Workflow Steps**:
1. Checkout repository
2. Set up Python 3.x
3. Install dependencies from requirements.txt
4. Run send_daily_chapter.py
5. Report success/failure

**Configuration**:
```yaml
on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily
  workflow_dispatch:      # Allow manual trigger for testing
```

## Setup Instructions (for README.md)

### Initial Setup (One-Time)
1. Clone this repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Place your EPUB file in the project directory
4. Run extraction: `python extract_epub.py your-book.epub`
5. Verify `chapters.json` was created with all chapters
6. Commit `chapters.json` to the repository

### GitHub Configuration
1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `BREVO_API_KEY`: Your Brevo API key
   - `SENDER_EMAIL`: Your verified sender email in Brevo
   - `SENDER_NAME`: Display name for sender (e.g., "Daily Book Reader")
   - `RECIPIENT_EMAIL`: Email to receive daily chapters
3. Enable GitHub Actions in the repository
4. Test with manual workflow trigger

### Brevo Setup
- Sign up for Brevo account (free tier: 300 emails/day)
- Go to Settings → SMTP & API → API Keys
- Create a new API key
- Verify your sender email address in Brevo
- Use API key in GitHub Secrets

## Dependencies (requirements.txt)
```
ebooklib==0.18
beautifulsoup4==4.12.2
lxml==4.9.3
sib-api-v3-sdk==7.6.0
```

## Optional Enhancements (Future)
- Support for multiple recipients
- HTML email formatting with better styling
- Option to include previous/next day teasers
- Weekly summary emails
- Support for different book formats (PDF, MOBI)
- Web interface to manage preferences

## Testing
- Test EPUB extraction with your specific book format
- Manually run `send_daily_chapter.py` locally before deploying
- Use workflow_dispatch to manually trigger GitHub Action
- Verify emails arrive with correct formatting

## Notes
- GitHub Actions has usage limits on free tier (2,000 minutes/month)
- This workflow uses <1 minute per day, well within limits
- EPUB file itself is NOT stored in repo (only extracted JSON)
- JSON file will be ~500KB-2MB depending on book length
- The system assumes 365 or 366 unique daily entries
- Brevo free tier allows 300 emails/day (more than sufficient for this use case)
- Brevo API is more reliable than SMTP for automated sending
- No need to manage app passwords or 2FA like with Gmail

## Customization
You can easily modify:
- Email send time (change cron schedule)
- Email subject/formatting (edit send script)
- Date format (modify key structure in JSON)
- Timezone (adjust cron schedule or add timezone handling)
