from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai

# Use APIRouter
router = APIRouter()

class FollowupRequest(BaseModel):
    api_key: str
    role: str
    company: str
    context: str
    delay_days: int
    tone: str

# Use the router decorator and a relative path
@router.post("/followup")
async def generate_followup(request: FollowupRequest):
    """
    Generates a follow-up email.
    """
    try:
        openai.api_key = request.api_key
        
        prompt = f"""
        Write a {request.tone} follow-up email to a {request.role} at {request.company}.

        Context of previous email: "{request.context}"
        
        This follow-up is being sent after {request.delay_days} days of no response. Be brief, professional, and add value if possible. Do not sound desperate.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in writing effective follow-up emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return {"followup_email": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))