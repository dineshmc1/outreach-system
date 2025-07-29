# api/maps_scraper.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from serpapi import GoogleSearch

# Use APIRouter
router = APIRouter()

# Define a Pydantic model to accept the request body
class MapsScrapeRequest(BaseModel):
    api_key: str
    keyword: str
    location: str

# CHANGE: This is now a POST endpoint to securely receive the API key
@router.post("/maps-scrape")
async def maps_scrape(request: MapsScrapeRequest):
    """
    Scrapes Google Maps for leads using the SerpApi service for reliability.
    The API key is provided in the request body.
    """
    if not request.api_key:
        raise HTTPException(
            status_code=400, 
            detail="SerpApi API Key is required."
        )

    params = {
        "engine": "google_local",
        "q": request.keyword,
        "location": request.location,
        "api_key": request.api_key  # Use the key from the request
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        local_results = results.get("local_results", [])

        if not local_results:
            return {"message": "No local results found for this query via SerpApi.", "leads": []}

        leads = []
        for result in local_results:
            leads.append({
                "name": result.get("title"),
                "website": result.get("website"),
                "phone": result.get("phone"),
                "address": result.get("address"),
                "rating": result.get("rating"),
                "niche": request.keyword
            })
            
        return {"leads": leads}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SerpApi scraping failed: {str(e)}")