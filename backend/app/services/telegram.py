import httpx
from app.core.config import settings

async def get_chat_id() -> str:
    """Fetches the chat ID of the last person who messaged the bot."""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
        # If the user has messaged the bot, grab their chat ID
        if data.get("ok") and data.get("result"):
            last_message = data["result"][-1]
            return str(last_message["message"]["chat"]["id"])
        return None

async def send_telegram_message(chat_id: str, text: str):
    """Sends a message to a specific chat ID."""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)