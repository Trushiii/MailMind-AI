import json
from pywebpush import webpush, WebPushException
from app.core.config import settings

def send_web_push(subscription_info: dict, title: str, body: str):
    """Sends a push notification to a specific browser subscription."""
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": "mailto:admin@mailmind.ai"}
        )
        return True
    except WebPushException as ex:
        print(f"Web Push failed: {ex}")
        return False