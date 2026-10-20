# ✨ MailMind AI

An advanced, AI-powered personal email intelligence application. MailMind AI connects to your Gmail account, analyzes your inbox using Google Gemini, extracts actionable tasks, prioritizes your emails, and delivers automated briefings directly to your phone.

Built with a modern **Neon/Glassmorphism** UI, this application runs entirely locally, ensuring complete privacy and zero hosting costs.

## 🚀 Features

- **Unified Inbox:** Connects securely to Gmail using OAuth 2.0 (read-only access).
- **AI Summarization & Categorization:** Uses Google Gemini to read emails, generate concise summaries, and categorize them (e.g., University, Job/Internship, Urgent).
- **Intelligent Prioritization:** Automatically assigns priority levels (Critical, High, Medium, Low) based on email context.
- **Task & Deadline Extraction:** Extracts actionable to-dos and due dates directly from email bodies.
- **Automated Reports:** Generates "Morning Briefing" and "Evening Review" reports.
- **Dual-Channel Notifications:**
  - **Telegram Bot:** Delivers AI-generated reports straight to your phone.
  - **Web Push:** Native browser notifications via Service Workers.
- **Automated Scheduling:** Uses APScheduler to automatically send reports at your chosen times.
- **Secure by Design:** OAuth tokens are encrypted at rest using Fernet cryptography. No data leaves your machine except to the official Google and Gemini APIs.

---

## 🛠️ Tech Stack

- **Frontend:** React, TypeScript, Vite, Custom CSS (Glassmorphism)
- **Backend:** Python 3, FastAPI, SQLAlchemy, Alembic, APScheduler
- **Database:** SQLite (default) or PostgreSQL (production-ready)
- **AI Engine:** Google Gemini API (`google-genai`)
- **Integrations:** Gmail API, Telegram Bot API, Web Push (VAPID)

---

## ⚙️ Local Setup Guide (Windows)

### 1. Prerequisites
Ensure you have the following installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js (LTS)](https://nodejs.org/)
- [Git](https://git-scm.com/)

### 2. Backend Setup

Open a terminal and navigate to the backend folder:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1