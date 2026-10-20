import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.core.config import settings
from app.core.security import decrypt_token, encrypt_token
from app.models.account import EmailAccount
from sqlalchemy.orm import Session

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_google_auth_url() -> str:
    flow = Flow.from_client_config(
        {"web": {"client_id": settings.gmail_client_id, "client_secret": settings.gmail_client_secret, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token"}},
        scopes=SCOPES, redirect_uri=settings.gmail_redirect_uri, autogenerate_code_verifier=False
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url

def exchange_code_for_tokens(code: str, db: Session) -> EmailAccount:
    flow = Flow.from_client_config(
        {"web": {"client_id": settings.gmail_client_id, "client_secret": settings.gmail_client_secret, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token"}},
        scopes=SCOPES, redirect_uri=settings.gmail_redirect_uri, autogenerate_code_verifier=False
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    service = build('gmail', 'v1', credentials=credentials)
    profile = service.users().getProfile(userId='me').execute()
    email_address = profile['emailAddress']

    account = db.query(EmailAccount).filter(EmailAccount.email_address == email_address).first()
    if not account:
        account = EmailAccount(email_address=email_address, provider="gmail")
        db.add(account)

    account.encrypted_access_token = encrypt_token(credentials.token)
    if credentials.refresh_token:
        account.encrypted_refresh_token = encrypt_token(credentials.refresh_token)
    if credentials.expiry:
        account.token_expires_at = credentials.expiry

    db.commit()
    db.refresh(account)
    return account

def get_gmail_service(account: EmailAccount) -> build:
    creds = Credentials(
        token=decrypt_token(account.encrypted_access_token),
        refresh_token=decrypt_token(account.encrypted_refresh_token),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        scopes=SCOPES
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)

def get_email_body(payload) -> str:
    """Extracts the plain text body from the Gmail payload."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8")
            elif "parts" in part:
                body += get_email_body(part) # Recursive for nested parts
    elif "body" in payload and "data" in payload["body"]:
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data).decode("utf-8")
    return body[:3000] # Limit to 3000 chars to save AI tokens