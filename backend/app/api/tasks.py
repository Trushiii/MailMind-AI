from email.message import EmailMessage

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.task import Task
from typing import Optional
from fastapi import APIRouter, Depends

router = APIRouter(tags=["tasks"])

@router.get("/")
def list_tasks(account_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if account_id:
        query = query.join(EmailMessage).filter(EmailMessage.account_id == account_id)
    return query.order_by(Task.id.desc()).all()