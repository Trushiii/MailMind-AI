from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.core.config import settings
from typing import List, Optional

client = genai.Client(api_key=settings.gemini_api_key)

class ExtractedTask(BaseModel):
    title: str = Field(description="Short action-oriented title")
    description: Optional[str] = Field(None, description="Detailed context")
    due_date: Optional[str] = Field(None, description="Due date if mentioned")
    priority: str = Field(description="Critical, High, Medium, Low")

class EmailAnalysis(BaseModel):
    summary: str = Field(description="Concise 1-2 sentence summary")
    category: str = Field(description="University, Job/Internship, Urgent, Newsletter, Personal, Other")
    priority: str = Field(description="Critical, High, Medium, Low")
    tasks: List[ExtractedTask] = Field(description="List of actionable tasks")

def analyze_email(sender: str, subject: str, body: str) -> EmailAnalysis:
    prompt = f"Sender: {sender}\nSubject: {subject}\nBody: {body}"
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',  # Stable, high free-tier limit
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EmailAnalysis
            )
        )
        return EmailAnalysis.model_validate_json(response.text)
    except Exception as e:
        print(f"AI ANALYSIS ERROR (Falling back to generic): {str(e)}")
        # Fallback so the sync NEVER crashes
        return EmailAnalysis(
            summary="AI summary temporarily unavailable due to API limits.",
            category="Other",
            priority="Low",
            tasks=[]
        )