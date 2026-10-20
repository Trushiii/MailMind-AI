from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.email import EmailMessage
from app.models.task import Task
from app.models.settings import UserSettings
from app.services.telegram import get_chat_id, send_telegram_message
from app.ai.reports import generate_report

router = APIRouter(tags=["reports"])

@router.post("/link-telegram")
async def link_telegram(db: Session = Depends(get_db)):
    chat_id = await get_chat_id()
    if not chat_id:
        raise HTTPException(status_code=400, detail="No messages found. Please send a message to your Telegram bot first.")
    
    settings = db.query(UserSettings).first()
    if not settings:
        settings = UserSettings(telegram_chat_id=chat_id)
        db.add(settings)
    else:
        settings.telegram_chat_id = chat_id
        
    db.commit()
    return {"status": "success", "message": f"Telegram linked successfully to chat {chat_id}"}

@router.post("/generate/{report_type}")
async def generate_and_send_report(report_type: str, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).first()
    if not settings or not settings.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram not linked. Please link it first.")

    emails = db.query(EmailMessage).order_by(EmailMessage.id.desc()).limit(10).all()
    tasks = db.query(Task).filter(Task.status == "pending").all()

    if not emails and not tasks:
        raise HTTPException(status_code=400, detail="No data to generate report.")

    report_text = generate_report(emails, tasks, report_type)
    await send_telegram_message(settings.telegram_chat_id, report_text)

    return {"status": "success", "message": f"{report_type} sent to Telegram!"}