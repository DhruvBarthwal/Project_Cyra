from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

gmail_service = None


def get_gmail_service():
    global gmail_service

    if gmail_service is not None:
        return gmail_service

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Gmail token...")
            creds.refresh(Request())
        else:
            print("Running Gmail OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(
                port=0,
                prompt="consent",
                access_type="offline",
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    gmail_service = build("gmail", "v1", credentials=creds)

    print("Gmail service initialized")

    return gmail_service