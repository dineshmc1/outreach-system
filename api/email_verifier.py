from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import dns.resolver
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerifyRequest(BaseModel):
    email: str

@app.post("/api/verify")
async def verify_email(request: VerifyRequest):
    """
    Verifies an email address using regex and MX record checks.
    """
    email = request.email
    
    # 1. Basic Regex Check
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return {"email": email, "is_valid": False, "reason": "Invalid syntax."}
        
    domain = email.split('@')[1]
    
    # 2. MX Record Check
    try:
        records = dns.resolver.resolve(domain, 'MX')
        if len(records) > 0:
            return {"email": email, "is_valid": True, "reason": "Syntax and domain are valid."}
        else:
            return {"email": email, "is_valid": False, "reason": "No MX records found for domain."}
    except dns.resolver.NoAnswer:
        return {"email": email, "is_valid": False, "reason": "No MX records found (NoAnswer)."}
    except dns.resolver.NXDOMAIN:
        return {"email": email, "is_valid": False, "reason": "Domain does not exist (NXDOMAIN)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
