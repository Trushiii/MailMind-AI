from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.scheduler import start_scheduler, shutdown_scheduler

from app.api.health import router as health_router
from app.api.accounts import router as accounts_router
from app.api.emails import router as emails_router
from app.api.tasks import router as tasks_router
from app.api.reports import router as reports_router
from app.api.notifications import router as notifications_router # <-- New import

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background scheduler
    start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    shutdown_scheduler()

# This line was missing or moved in your file
app = FastAPI(title="MailMind AI API", version="0.8.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(accounts_router, prefix="/api/accounts")
app.include_router(emails_router, prefix="/api/emails")
app.include_router(tasks_router, prefix="/api/tasks")
app.include_router(reports_router, prefix="/api/reports")
app.include_router(notifications_router, prefix="/api/notifications") # <-- New route

@app.get("/")
def root():
    return {"message": "MailMind AI API is running with Scheduler and Web Push"}