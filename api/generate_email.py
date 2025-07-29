from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai

# Use APIRouter instead of FastAPI
router = APIRouter()

class EmailRequest(BaseModel):
    api_key: str
    name: str
    role: str
    company: str
    pain_point: str
    offer: str
    tone: str

# Use the router decorator and a relative path
@router.post("/generate")
async def generate_email(request: EmailRequest):
    """
    Generates a single cold email using GPT-4o.
    """
    try:
        openai.api_key = request.api_key
        
        prompt = f"""
        You're an expert in cold outreach. Write a short, punchy cold email to {request.role} at {request.company}.

        Pain: {request.pain_point}
        Offer: {request.offer}
        Tone: {request.tone}

        Use the name {request.name} in the greeting. No fluff. One clear Call-To-Action. Keep it under 120 words.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class cold email copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        return {"email": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))