from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.database.session import get_db
from app.models.account import EmailAccount
from app.models.email import EmailMessage
from app.models.task import Task
from app.providers.gmail import get_gmail_service, get_email_body
from app.ai.gemini_client import analyze_email

# This line was missing!
router = APIRouter(tags=["emails"])

@router.get("/")
def list_emails(account_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(EmailMessage)
    if account_id:
        query = query.filter(EmailMessage.account_id == account_id)
    return query.order_by(EmailMessage.id.desc()).limit(20).all()

@router.post("/sync/{account_id}")
def sync_emails(account_id: int, db: Session = Depends(get_db)):
    account = db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    service = get_gmail_service(account)
    
    try:
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])

        for msg in messages:
            exists = db.query(EmailMessage).filter_by(account_id=account.id, provider_message_id=msg['id']).first()
            if not exists:
                msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_detail['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown")
                snippet = msg_detail.get('snippet', '')
                body_text = get_email_body(msg_detail['payload'])
                
                ai_result = analyze_email(sender=sender, subject=subject, body=body_text)
                
                new_email = EmailMessage(
                    account_id=account.id,
                    provider_message_id=msg['id'],
                    thread_id=msg_detail.get('threadId'),
                    subject=subject,
                    sender=sender,
                    snippet=snippet,
                    received_at=datetime.utcnow(),
                    ai_summary=ai_result.summary,
                    ai_category=ai_result.category,
                    ai_priority=ai_result.priority
                )
                
                try:
                    db.add(new_email)
                    db.flush()

                    for t in ai_result.tasks:
                        new_task = Task(
                            email_id=new_email.id,
                            title=t.title,
                            description=t.description,
                            due_date=t.due_date,
                            priority=t.priority
                        )
                        db.add(new_task)
                except IntegrityError:
                    db.rollback()
                    continue
        
        db.commit()
        return {"status": "success", "message": "Emails synced and analyzed"}
    except Exception as e:
        db.rollback()
        print(f"SYNC ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")