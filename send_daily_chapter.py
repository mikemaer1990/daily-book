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

    # Split content into paragraphs and wrap in <p> tags
    paragraphs = chapter_content.split('\n\n')
    html_paragraphs = ''.join(f'<p>{p}</p>' for p in paragraphs if p.strip())

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Georgia, serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            p {{
                margin-bottom: 15px;
                text-align: justify;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Your Daily Reading - {readable_date}</h1>
            {html_paragraphs}
            <div class="footer">
                <p>Daily Book Emailer</p>
            </div>
        </div>
    </body>
    </html>
    """

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
