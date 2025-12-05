#!/usr/bin/env python3
"""
Daily Chapter Email Sender
Sends today's chapter via Brevo API
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()


def load_chapters(chapters_file='chapters.json'):
    """Load chapters from JSON file."""
    if not Path(chapters_file).exists():
        print(f"Error: {chapters_file} not found!")
        print("Please run extract_epub.py first to generate the chapters file.")
        sys.exit(1)

    with open(chapters_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_todays_chapter(chapters):
    """Get the chapter for today's date."""
    today = datetime.now().strftime('%m-%d')
    print(f"Looking for chapter for date: {today}")

    if today not in chapters:
        print(f"Warning: No chapter found for {today}")
        return None, today

    return chapters[today], today


def format_email_html(chapter_content, date_str):
    """Format chapter content as HTML email."""
    # Convert date to readable format (add current year to avoid deprecation warning)
    current_year = datetime.now().year
    date_obj = datetime.strptime(f"{current_year}-{date_str}", '%Y-%m-%d')
    readable_date = date_obj.strftime('%B %d')

    # Process paragraphs and detect author attributions
    paragraphs = chapter_content.split('\n\n')
    html_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            continue

        # Check if this is an author attribution (starts with — or --)
        if para.strip().startswith('—') or para.strip().startswith('--'):
            # Author attribution - style differently
            author = para.strip().lstrip('—').lstrip('-').strip()
            html_paragraphs.append(f'<p class="author">— {author}</p>')
        else:
            # Regular paragraph
            html_paragraphs.append(f'<p class="quote">{para.strip()}</p>')

    html_paragraphs_str = ''.join(html_paragraphs)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Email-safe CSS */
        body {{
            margin: 0;
            padding: 0;
            font-family: Georgia, 'Times New Roman', serif;
            background-color: #f5f5f0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .email-wrapper {{
            width: 100%;
            background-color: #f5f5f0;
            padding: 20px 0;
        }}

        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .header {{
            background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
            padding: 32px 40px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            padding: 0;
            color: #ffffff;
            font-size: 26px;
            font-weight: 400;
            letter-spacing: 0.5px;
            line-height: 1.3;
        }}

        .subheader {{
            margin: 8px 0 0 0;
            padding: 0;
            color: #f5f5f0;
            font-size: 13px;
            font-weight: 300;
            letter-spacing: 1px;
            text-transform: uppercase;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px 40px 32px 40px;
            color: #2c2c2c;
            line-height: 1.8;
        }}

        .quote {{
            margin: 0 0 20px 0;
            padding: 0;
            font-size: 16px;
            color: #2c2c2c;
            text-align: left;
        }}

        .author {{
            margin: -8px 0 28px 0;
            padding: 0;
            font-size: 14px;
            color: #8b7355;
            font-style: italic;
            text-align: left;
            font-weight: 500;
        }}

        .divider {{
            margin: 32px auto;
            width: 60px;
            height: 1px;
            background-color: #d4c5b9;
        }}

        .footer {{
            padding: 24px 40px 32px 40px;
            background-color: #fafaf8;
            border-top: 1px solid #e8e8e0;
            text-align: center;
        }}

        .footer-text {{
            margin: 0;
            padding: 0;
            font-size: 13px;
            color: #8b8b8b;
            font-style: italic;
        }}

        .footer-book {{
            margin: 8px 0 0 0;
            padding: 0;
            font-size: 11px;
            color: #a8a8a8;
            letter-spacing: 0.5px;
        }}

        /* Mobile responsiveness */
        @media only screen and (max-width: 600px) {{
            .container {{
                border-radius: 0;
            }}
            .header {{
                padding: 28px 24px;
            }}
            .header h1 {{
                font-size: 22px;
            }}
            .content {{
                padding: 32px 24px 24px 24px;
            }}
            .quote {{
                font-size: 15px;
            }}
            .footer {{
                padding: 20px 24px 28px 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="container">
            <div class="header">
                <h1>Your Daily Reading</h1>
                <p class="subheader">{readable_date}</p>
            </div>

            <div class="content">
                {html_paragraphs_str}
            </div>

            <div class="footer">
                <p class="footer-text">A moment of wisdom to start your day</p>
                <p class="footer-book">From "A Calendar of Wisdom" by Leo Tolstoy</p>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_content


def send_email(api_key, sender_email, sender_name, recipient_email, subject, html_content):
    """Send email via Brevo API."""
    # Configure API key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    # Create API instance
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare email
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": recipient_email}],
        sender={"email": sender_email, "name": sender_name},
        subject=subject,
        html_content=html_content
    )

    try:
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent successfully!")
        print(f"Message ID: {api_response.message_id}")
        return True

    except ApiException as e:
        print(f"Error sending email: {e}")
        return False


def send_error_notification(api_key, sender_email, sender_name, recipient_email, date_str):
    """Send notification email when chapter is not found."""
    subject = f"Daily Reading - No Chapter Found for {date_str}"

    current_year = datetime.now().year
    date_obj = datetime.strptime(f"{current_year}-{date_str}", '%Y-%m-%d')
    readable_date = date_obj.strftime('%B %d')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                max-width: 600px;
                margin: 0 auto;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                padding: 20px;
                border-radius: 5px;
            }}
            h2 {{ color: #856404; }}
        </style>
    </head>
    <body>
        <div class="warning">
            <h2>No Chapter Available</h2>
            <p>Unfortunately, no chapter was found for today's date: <strong>{readable_date}</strong> ({date_str}).</p>
            <p>This could mean:</p>
            <ul>
                <li>The book doesn't have a reading for this specific date</li>
                <li>The extraction process missed this date</li>
                <li>There's an issue with the chapters.json file</li>
            </ul>
            <p>Please check your chapters.json file and ensure it contains an entry for "{date_str}".</p>
        </div>
    </body>
    </html>
    """

    print("Sending error notification...")
    return send_email(api_key, sender_email, sender_name, recipient_email, subject, html_content)


def main():
    # Get environment variables
    api_key = os.environ.get('BREVO_API_KEY')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_name = os.environ.get('SENDER_NAME', 'Daily Book Reader')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')

    # Validate environment variables
    missing_vars = []
    if not api_key:
        missing_vars.append('BREVO_API_KEY')
    if not sender_email:
        missing_vars.append('SENDER_EMAIL')
    if not recipient_email:
        missing_vars.append('RECIPIENT_EMAIL')

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your GitHub Secrets or environment.")
        sys.exit(1)

    print("="*60)
    print("Daily Chapter Email Sender")
    print("="*60)

    # Load chapters
    chapters = load_chapters()
    print(f"Loaded {len(chapters)} chapters from chapters.json")

    # Get today's chapter
    chapter_content, date_str = get_todays_chapter(chapters)

    if chapter_content is None:
        # Send error notification
        success = send_error_notification(api_key, sender_email, sender_name, recipient_email, date_str)
        sys.exit(0 if success else 1)

    # Format email
    current_year = datetime.now().year
    date_obj = datetime.strptime(f"{current_year}-{date_str}", '%Y-%m-%d')
    readable_date = date_obj.strftime('%B %d')
    subject = f"Your Daily Reading - {readable_date}"

    print(f"Preparing email: {subject}")
    print(f"Chapter length: {len(chapter_content)} characters")

    html_content = format_email_html(chapter_content, date_str)

    # Send email
    print(f"\nSending to: {recipient_email}")
    print(f"From: {sender_name} <{sender_email}>")

    success = send_email(api_key, sender_email, sender_name, recipient_email, subject, html_content)

    if success:
        print("\n" + "="*60)
        print("Daily chapter sent successfully!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("Failed to send daily chapter")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
