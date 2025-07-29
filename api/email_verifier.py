from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import dns.resolver
import re

# Use APIRouter
router = APIRouter()

class VerifyRequest(BaseModel):
    email: str

# Use the router decorator and a relative path
@router.post("/verify")
async def verify_email(request: VerifyRequest):
    """
    Verifies an email address using regex and MX record checks.
    """
    email = request.email
    
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return {"email": email, "is_valid": False, "reason": "Invalid syntax."}
        
    domain = email.split('@')[1]
    
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