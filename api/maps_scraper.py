from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A more robust User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

def find_email_on_site(url):
    """
    Scrapes a website to find an email address.
    """
    try:
        if not url.startswith('http'):
            url = 'http://' + url
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        
        # Regex to find emails
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, response.text)
        
        # Filter out common false positives
        valid_emails = [email for email in emails if not email.endswith(('.png', '.jpg', '.gif', '.svg'))]
        
        return valid_emails[0] if valid_emails else "Not Found"
    except (requests.RequestException, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
        print(f"Could not fetch {url}: {e}")
        return "Website Unreachable"

@app.get("/api/maps-scrape")
async def maps_scrape(keyword: str, location: str):
    """
    Scrapes Google Maps for business leads.
    This is a simplified example. Real Google Maps scraping is complex and
    often requires more advanced tools like Selenium or dedicated APIs.
    """
    try:
        query = f"{keyword} in {location}"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        leads = []
        # This selector is generic and might need updates if Google changes its structure
        for result in soup.select('.tF2Cxc, .g'): 
            name_tag = result.select_one('h3')
            link_tag = result.select_one('a')
            website_tag = result.select_one('cite')
            
            if name_tag and link_tag and website_tag:
                name = name_tag.get_text()
                website_url = link_tag['href']
                
                # Try to extract a clean website domain
                clean_website = website_tag.get_text().split(' ')[0]
                
                if 'google.com' not in website_url: # Filter out irrelevant links
                    email = find_email_on_site(clean_website)
                    leads.append({
                        "name": name,
                        "website": clean_website,
                        "email": email,
                        "niche": keyword,
                        "source": "Google Search"
                    })
        
        if not leads:
            return {"message": "No results found. Google might be blocking the request or the page structure has changed. This scraper is for demonstration purposes.", "leads": []}
            
        return {"leads": leads[:5]} # Return top 5 results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")