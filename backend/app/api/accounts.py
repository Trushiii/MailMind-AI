from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.providers.gmail import get_google_auth_url, exchange_code_for_tokens
from app.core.config import settings
from app.models.account import EmailAccount

# This line must be here so the routes can attach to it
router = APIRouter(tags=["accounts"])

@router.get("/")
def list_accounts(db: Session = Depends(get_db)):
    """Returns all connected email accounts."""
    return db.query(EmailAccount).all()

@router.get("/gmail/connect")
def connect_gmail():
    """Returns the Google OAuth URL for the frontend to redirect to."""
    return {"auth_url": get_google_auth_url()}

@router.get("/gmail/callback")
def gmail_callback(code: str, db: Session = Depends(get_db)):
    """Handles the redirect from Google."""
    try:
        exchange_code_for_tokens(code, db)
        # Redirect back to frontend
        return RedirectResponse(url=f"{settings.frontend_url}?connected=true")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")