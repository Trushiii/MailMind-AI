from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.database.session import SessionLocal
from app.models.email import EmailMessage
from app.models.task import Task
from app.models.settings import UserSettings
from app.models.push import PushSubscription
from app.services.telegram import send_telegram_message
from app.services.push import send_web_push
from app.ai.reports import generate_report
import asyncio

# Initialize the scheduler
scheduler = AsyncIOScheduler(timezone=settings.timezone)

def run_automated_report(report_type: str):
    """Background job that runs on a schedule."""
    print(f"⏰ [SCHEDULER] Starting automated {report_type} generation...")
    
    # We must create a new DB session for background tasks
    db = SessionLocal()
    try:
        user_settings = db.query(UserSettings).first()
        
        # Fetch recent emails and pending tasks
        emails = db.query(EmailMessage).order_by(EmailMessage.id.desc()).limit(10).all()
        tasks = db.query(Task).filter(Task.status == "pending").all()

        if not emails and not tasks:
            print(f"⚠️ [SCHEDULER] Skipping {report_type}: No emails or tasks found.")
            return

        # Generate report (using the fallback-safe function we built)
        report_text = generate_report(emails, tasks, report_type)

        # 1. Send to Telegram (if linked)
        if user_settings and user_settings.telegram_chat_id:
            asyncio.run(send_telegram_message(user_settings.telegram_chat_id, report_text))
            print(f"✅ [SCHEDULER] Successfully sent {report_type} to Telegram.")
        else:
            print(f"⚠️ [SCHEDULER] Telegram not linked. Skipping Telegram delivery.")

        # 2. Send Web Push to all subscribed browsers
        subs = db.query(PushSubscription).all()
        if subs:
            for sub in subs:
                sub_info = {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}}
                send_web_push(sub_info, f"MailMind AI: {report_type}", "Your new report is ready! Open the app to read it.")
            print(f"✅ [SCHEDULER] Sent {report_type} to {len(subs)} Web Push devices.")
        else:
            print(f"⚠️ [SCHEDULER] No browsers subscribed to Web Push.")

    except Exception as e:
        print(f"❌ [SCHEDULER ERROR] Failed to run {report_type}: {str(e)}")
    finally:
        db.close()

def start_scheduler():
    """Sets up the cron jobs based on .env times and starts the scheduler."""
    # Parse "HH:MM" strings into hour and minute
    m_hour, m_minute = map(int, settings.morning_report_time.split(":"))
    e_hour, e_minute = map(int, settings.evening_report_time.split(":"))

    # Add Morning Briefing Job
    scheduler.add_job(
        run_automated_report,
        trigger=CronTrigger(hour=m_hour, minute=m_minute, timezone=settings.timezone),
        args=["Morning Briefing"],
        id="morning_briefing",
        replace_existing=True
    )

    # Add Evening Review Job
    scheduler.add_job(
        run_automated_report,
        trigger=CronTrigger(hour=e_hour, minute=e_minute, timezone=settings.timezone),
        args=["Evening Review"],
        id="evening_review",
        replace_existing=True
    )

    scheduler.start()
    print(f"🚀 Scheduler started. Morning: {settings.morning_report_time}, Evening: {settings.evening_report_time} ({settings.timezone})")

def shutdown_scheduler():
    scheduler.shutdown()
    print("🛑 Scheduler stopped.")