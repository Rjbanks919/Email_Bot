"""
bot.py

This script polls a GMail inbox for commands and responds accordingly.

Functions:
    get_header_value
    authenticate_gmail
    get_latest_email
    download_image
    send_response_email
    parse_command
    main

Usage:
    Make sure you have your credentials.json file placed at /opt/Email_Bot/
    before running the script!

    $ python3 bot.py
"""

# Standard library includes
import re
import os
import base64
import mimetypes

# Email-based library includes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Google library includes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Other library includes
import requests


# Your Gmail API credentials JSON file
CREDENTIALS_PATH = "/opt/Email_Bot/credentials.json"
TOKEN_PATH = "/opt/Email_Bot/token.json"

# If modifying these scopes, delete the file token.json.
OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

# This is the email that the bot will respond to commands from
ALLOWED_USER = '<YOUR_EMAIL_HERE>'


def get_header_value(payload, header_name: str) -> str:
    """
    Retrieves a value out of the email data header.

    Args:
        payload (?): Email payload containing headers.
        header_name (str): Name of the header to find.

    Returns:
        str: The value associated with the header.
    """
    for header in payload['headers']:
        if header['name'] == header_name:
            return header['value']

    return None


def authenticate_gmail():
    """
    Authenticates the script using provided credentials/token.

    Note:
        If a token does not exist, it will begin the generation process.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, OAUTH_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_latest_email(service):
    """
    Retrieves the newest email in the bot's email inbox.

    Args:
        service (?): Email service handle?

    Returns:
        (str, str): Tuple containing email sender and subject.
    """
    # Get the latest email
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    latest_email_id = messages[0]['id']
    message = service.users().messages().get(userId='me', id=latest_email_id).execute()

    if message:
        sender = get_header_value(message['payload'], 'From')
        subject = get_header_value(message['payload'], 'Subject')

        service.users().messages().trash(userId='me', id=latest_email_id).execute()

        return (sender, subject)

    return None


def download_image(image_url, save_path):
    """
    Downloads an image from a provided URL.

    Args:
        image_url (str): URL of the image to download.
        save_path (str): Path to save the downloaded image to.
    """
    # Download the image from the URL
    response = requests.get(image_url)

    with open(save_path, 'wb') as file:
        file.write(response.content)


def send_response_email(to_address, subject, body, attachment_paths=None):
    """
    Sends a response email containing requested data.

    Args:
        to_address (str): Email address to send to.
        subject (str): Subject of the email.
        body (?): Body of the email.
        attachment_paths (list(str)): Paths to attachments for the email.
    """
    creds = authenticate_gmail()  # Make sure this function is properly implemented

    msg = MIMEMultipart()
    msg['From'] = creds._client_id
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment_paths:
        for attachment_path in attachment_paths:
            content_type, encoding = mimetypes.guess_type(attachment_path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            with open(attachment_path, 'rb') as attachment:
                image = MIMEImage(attachment.read(), _subtype=sub_type)
                image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(image)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')}
        service.users().messages().send(userId='me', body=message).execute()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", str(e))


def parse_command(sender_subject):
    """
    Parses a command from an email subject line.

    Args:
        sender_subject (str): Subject of the received command email.

    Returns:
        str: Parsed command.
    """
    pattern = r"^cmd: (\w+)$"

    match = re.search(pattern, sender_subject[1])

    if sender_subject[0] == ALLOWED_USER and match:
        command = match.group(1)
        return command
    else:
        return None


def main():
    """
    Main function bro, are you a cop?
    """
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Get the latest email
    sender_subject = get_latest_email(service)

    if sender_subject:
        # Tuple is
        command = parse_command(sender_subject)

        print(command)

        if command == "send_cams":
            front_url = "<URL_HERE>"
            back_url = "<URL_HERE>"

            front_save_path = './front-porch.jpg'
            back_save_path = './back-yard.jpg'
            download_image(front_url, front_save_path)
            download_image(back_url, back_save_path)

            # Send a response email with the downloaded image attached
            to_email = '<YOUR_EMAIL_HERE>'
            email_subject = 'Response with Image'
            email_body = 'Here is the image you requested!'
            send_response_email(to_email, email_subject, email_body, [front_save_path, back_save_path])


if __name__ == '__main__':
    main()

