# Daily Book Emailer

A lightweight automation system that extracts daily chapters from an EPUB file and automatically emails them via GitHub Actions and Brevo API.

## Features

- Extract daily chapters from EPUB files into a structured JSON format
- Automatic daily email delivery at 6:00 AM PST/PDT
- Beautiful HTML-formatted emails
- Error notifications if a chapter is missing
- Free to run using GitHub Actions and Brevo's free tier

## Tech Stack

- **Language**: Python 3.11
- **EPUB Parsing**: ebooklib and BeautifulSoup4
- **Email Service**: Brevo (formerly Sendinblue) API
- **Automation**: GitHub Actions
- **Data Storage**: JSON file (committed to repository)

## Initial Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Extract Chapters from EPUB

Place your EPUB file in the project directory, then run:

```bash
python extract_epub.py your-book.epub
```

This will:
- Parse the EPUB file
- Automatically detect dates in chapter titles
- Extract and clean the text content
- Save everything to `chapters.json`

The script handles various date formats:
- "January 1", "Jan 1"
- "1 January", "1st January"
- "Day 1" (sequential)

**Example output:**
```
Opening EPUB file: my-daily-devotional.epub

Found 365 document items in EPUB
Extracting chapters...

✓ [1/365] 01-01: January 1 - New Beginnings...
✓ [2/365] 01-02: January 2 - Daily Strength...
...

Extraction complete!
Total chapters extracted: 365
Items skipped: 12

Chapters saved to: chapters.json
Date range: 01-01 to 12-31
Average chapter length: 1247 characters
```

### 3. Review and Commit

1. Open `chapters.json` to verify all dates are present (01-01 through 12-31)
2. Add the file to your repository:

```bash
git add chapters.json
git commit -m "Add extracted daily chapters"
git push
```

## Brevo Setup

1. Sign up for a free Brevo account at [brevo.com](https://www.brevo.com)
   - Free tier includes 300 emails/day (more than enough)

2. Verify your sender email address:
   - Go to **Settings** → **Senders & IP**
   - Add and verify your sender email

3. Get your API key:
   - Go to **Settings** → **SMTP & API** → **API Keys**
   - Click **Create a new API Key**
   - Copy the key (you won't see it again!)

## GitHub Configuration

### Set Up Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of the following:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `BREVO_API_KEY` | Your Brevo API key | `xkeysib-abc123...` |
| `SENDER_EMAIL` | Verified sender email in Brevo | `noreply@yourdomain.com` |
| `SENDER_NAME` | Display name for sender | `Daily Book Reader` |
| `RECIPIENT_EMAIL` | Your email address | `you@example.com` |

### Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will automatically run daily at 6:00 AM PST/PDT

## Testing

### Test Locally

Before deploying, test the email sending locally:

```bash
# Set environment variables (Windows)
set BREVO_API_KEY=your-api-key-here
set SENDER_EMAIL=your-sender@example.com
set SENDER_NAME=Daily Book Reader
set RECIPIENT_EMAIL=your-email@example.com

# Run the script
python send_daily_chapter.py
```

For macOS/Linux:
```bash
export BREVO_API_KEY=your-api-key-here
export SENDER_EMAIL=your-sender@example.com
export SENDER_NAME="Daily Book Reader"
export RECIPIENT_EMAIL=your-email@example.com

python send_daily_chapter.py
```

### Test GitHub Action

1. Go to **Actions** tab in your GitHub repository
2. Select **Send Daily Chapter Email** workflow
3. Click **Run workflow** → **Run workflow**
4. Check your email inbox

## How It Works

### Daily Schedule

The GitHub Action runs automatically at **6:00 AM PST/PDT** every day:
- Checks out the repository
- Installs Python dependencies
- Runs `send_daily_chapter.py`
- Sends the chapter for today's date

### Email Format

Emails are sent as beautifully formatted HTML with:
- Clear subject line: "Your Daily Reading - January 1"
- Readable serif font (Georgia)
- Proper paragraph spacing
- Mobile-friendly responsive design
- Clean, distraction-free layout

### Error Handling

If no chapter exists for today's date:
- You'll receive a notification email explaining the issue
- The workflow will complete successfully (no false alarms)

## Project Structure

```
daily-book/
├── extract_epub.py              # One-time EPUB extraction script
├── send_daily_chapter.py        # Daily email sender script
├── chapters.json                # Extracted chapters (generated)
├── requirements.txt             # Python dependencies
├── .github/
│   └── workflows/
│       └── daily-email.yml      # GitHub Actions workflow
└── README.md                    # This file
```

## Timezone Notes

The workflow is configured for **PST/PDT (Pacific Time)**:
- PST (Winter): 6:00 AM PST = 14:00 UTC
- PDT (Summer): 6:00 AM PDT = 13:00 UTC

The cron schedule uses `14:00 UTC` which works for PST. During PDT, emails arrive at 7:00 AM instead of 6:00 AM. If you need exact timing year-round, you'll need to manually adjust the cron schedule twice a year, or implement timezone-aware scheduling.

To change the send time, edit `.github/workflows/daily-email.yml`:
```yaml
- cron: '0 14 * * *'  # Change hour (0-23 UTC)
```

## Customization

### Change Email Subject

Edit `send_daily_chapter.py` around line 145:
```python
subject = f"Your Daily Reading - {readable_date}"
```

### Modify Email Styling

Edit the CSS in the `format_email_html()` function in `send_daily_chapter.py`.

### Add Multiple Recipients

Modify `send_email()` in `send_daily_chapter.py`:
```python
to=[
    {"email": "person1@example.com"},
    {"email": "person2@example.com"}
]
```

## Troubleshooting

### Extraction Issues

**Problem**: Some chapters weren't extracted
- Check the EPUB file structure - titles may not contain recognizable dates
- Review the "Skipped items" in extraction output
- You may need to manually edit `chapters.json`

### Email Not Sending

**Problem**: Workflow runs but no email arrives

1. Check GitHub Actions logs for errors
2. Verify all secrets are set correctly
3. Ensure sender email is verified in Brevo
4. Check your spam folder
5. Verify Brevo API key is valid

**Problem**: "Invalid API key" error
- Make sure you copied the full API key from Brevo
- Ensure no extra spaces in the GitHub secret
- Generate a new API key if needed

### Wrong Send Time

The workflow runs at 14:00 UTC (6 AM PST):
- During PST (winter): Emails arrive at 6:00 AM Pacific
- During PDT (summer): Emails arrive at 7:00 AM Pacific

To adjust, modify the cron schedule in `.github/workflows/daily-email.yml`.

## Cost and Limits

- **GitHub Actions**: 2,000 minutes/month (free tier)
  - This workflow uses ~1 minute/day = ~30 minutes/month
- **Brevo**: 300 emails/day (free tier)
  - This system sends 1 email/day

Both are well within free tier limits.

## Privacy

- Your EPUB file is NOT stored in the repository
- Only extracted text chapters are saved in `chapters.json`
- All emails are sent via Brevo's secure API
- No data is collected or stored outside your GitHub repository

## License

MIT License - feel free to use and modify for your own purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub Actions logs for error messages
3. Verify Brevo account status and API key validity

---

**Enjoy your daily readings!**
