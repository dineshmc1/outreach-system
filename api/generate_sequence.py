from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai

# Use APIRouter
router = APIRouter()

class SequenceRequest(BaseModel):
    api_key: str
    name: str
    role: str
    company: str
    pain_point: str
    offer: str
    tone: str

# Use the router decorator and a relative path
@router.post("/sequence")
async def generate_sequence(request: SequenceRequest):
    """
    Generates a 3-email sequence (cold email + 2 follow-ups).
    """
    try:
        openai.api_key = request.api_key
        
        # 1. Generate Cold Email
        cold_email_prompt = f"Write a short, punchy cold email to {request.role} at {request.company}, named {request.name}. Pain point: {request.pain_point}. Offer: {request.offer}. Tone: {request.tone}. One CTA."
        cold_email_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": cold_email_prompt}],
            temperature=0.7, max_tokens=200
        )
        cold_email = cold_email_response.choices[0].message.content.strip()

        # 2. Generate Follow-Up 1
        follow_up_1_prompt = f"Write a brief, {request.tone} follow-up to the previous email. Context: Sent a cold email about '{request.offer}' to address '{request.pain_point}'. This is sent 3 days later. Add a small piece of value or a different angle."
        follow_up_1_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": follow_up_1_prompt}],
            temperature=0.7, max_tokens=150
        )
        follow_up_1 = follow_up_1_response.choices[0].message.content.strip()

        # 3. Generate Follow-Up 2 (Breakup Email)
        follow_up_2_prompt = f"Write a final, short, professional 'breakup' email. The goal is to close the loop gracefully. Context: Sent two previous emails about '{request.offer}'. This is the last message. Keep it polite and simple."
        follow_up_2_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": follow_up_2_prompt}],
            temperature=0.7, max_tokens=100
        )
        follow_up_2 = follow_up_2_response.choices[0].message.content.strip()

        sequence = [
            {"step": 1, "delay_days": 0, "subject": f"Quick Question for {request.company}", "body": cold_email},
            {"step": 2, "delay_days": 3, "subject": f"Re: Quick Question", "body": follow_up_1},
            {"step": 3, "delay_days": 7, "subject": f"Re: Quick Question", "body": follow_up_2},
        ]

        return {"sequence": sequence}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))