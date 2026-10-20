from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.session import get_db
from app.models.push import PushSubscription
from app.core.config import settings
from app.services.push import send_web_push

router = APIRouter(tags=["notifications"])

class SubscriptionData(BaseModel):
    endpoint: str
    keys: dict

@router.get("/vapid-public-key")
def get_vapid_key():
    return {"publicKey": settings.vapid_public_key}

@router.post("/subscribe")
def subscribe(sub_data: SubscriptionData, db: Session = Depends(get_db)):
    exists = db.query(PushSubscription).filter_by(endpoint=sub_data.endpoint).first()
    if not exists:
        new_sub = PushSubscription(
            endpoint=sub_data.endpoint,
            p256dh=sub_data.keys.get("p256dh"),
            auth=sub_data.keys.get("auth")
        )
        db.add(new_sub)
        db.commit()
    return {"status": "success", "message": "Subscribed to push notifications"}

@router.post("/test-push")
def test_push(db: Session = Depends(get_db)):
    subs = db.query(PushSubscription).all()
    if not subs:
        raise HTTPException(status_code=400, detail="No browsers subscribed.")
    
    success_count = 0
    for sub in subs:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
        }
        if send_web_push(sub_info, "MailMind AI Test", "Web Push is working perfectly! 🎉"):
            success_count += 1
            
    return {"status": "success", "message": f"Sent to {success_count} devices."}