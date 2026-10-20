import time
from google import genai
from app.core.config import settings
from app.models.email import EmailMessage
from app.models.task import Task
from typing import List
from fastapi import HTTPException

client = genai.Client(api_key=settings.gemini_api_key)

def generate_report(emails: List[EmailMessage], tasks: List[Task], report_type: str) -> str:
    email_data = "\n".join([
        f"- {getattr(e, 'subject', 'No Subject')} (Priority: {getattr(e, 'ai_priority', 'Medium')}): {getattr(e, 'ai_summary', 'No summary')}" 
        for e in emails
    ])
    
    task_data = "\n".join([
        f"- {getattr(t, 'title', 'Unknown Task')} (Due: {getattr(t, 'due_date', 'None')}, Priority: {getattr(t, 'priority', 'Medium')})" 
        for t in tasks
    ])
    
    prompt = f"""
    You are MailMind AI. Generate a {report_type} report for the user.
    Emails: {email_data}
    Tasks: {task_data}
    Format this as a clean, readable Telegram message using emojis. Keep it concise.
    """
    
    # Try up to 3 times to get an AI response
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"AI REPORT ERROR (Attempt {attempt+1}/3): {str(e)}")
            if attempt < 2:
                time.sleep(3) # Wait 3 seconds before trying again
            else:
                # If Google's servers are completely down, generate a fallback text report
                print("All AI attempts failed. Sending raw fallback report.")
                fallback_text = f"📊 *{report_type}*\n\n"
                fallback_text += "⚠️ _Google AI is currently overloaded. Here is your raw data:_\n\n"
                
                if emails:
                    fallback_text += "📥 *Recent Emails:*\n"
                    for e in emails[:3]: # Show top 3
                        fallback_text += f"- {getattr(e, 'subject', 'No Subject')} ({getattr(e, 'ai_priority', 'Low')})\n"
                
                if tasks:
                    fallback_text += "\n✅ *Pending Tasks:*\n"
                    for t in tasks[:3]: # Show top 3
                        fallback_text += f"- {getattr(t, 'title', 'Task')} (Due: {getattr(t, 'due_date', 'None')})\n"
                
                return fallback_text