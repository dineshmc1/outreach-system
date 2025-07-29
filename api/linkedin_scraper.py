from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from linkedin_scraper import Person, Linkedin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinkedinScrapeRequest(BaseModel):
    profile_url: str
    email: str
    password: str

@app.post("/api/linkedin-scrape")
async def linkedin_scrape(request: LinkedinScrapeRequest):
    """
    Scrapes a LinkedIn profile using credentials passed directly from the frontend.
    
    SECURITY WARNING: This method is insecure and exposes credentials.
    It is implemented for demonstration purposes only. Use at your own extreme risk.
    """
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="LinkedIn email and password are required.")

    try:
        # Authenticate using credentials from the request body.
        api = Linkedin(request.email, request.password)
        person = Person(request.profile_url, api=api, close_on_complete=True)

        scraped_data = {
            "full_name": person.name,
            "job_title": person.job_title,
            "company": person.company,
            "location": person.location,
            "about_section": person.about,
            "profile_url": request.profile_url,
            "status": "Success (Live Scraped Data)"
        }
        
        return scraped_data

    except Exception as e:
        print(f"An error occurred during LinkedIn scraping: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to scrape LinkedIn profile. Check your credentials or the profile URL. LinkedIn might be blocking the request. Original error: {str(e)}"
        )