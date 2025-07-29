from fastapi import APIRouter, HTTPException
import requests
from bs4 import BeautifulSoup
import re

# Use APIRouter
router = APIRouter()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

def find_email_on_site(url):
    try:
        if not url.startswith('http'):
            url = 'http://' + url
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, response.text)
        
        valid_emails = [email for email in emails if not email.endswith(('.png', '.jpg', '.gif', '.svg'))]
        
        return valid_emails[0] if valid_emails else "Not Found"
    except requests.RequestException:
        return "Website Unreachable"

# Use the router decorator and a relative path
@router.get("/maps-scrape")
async def maps_scrape(keyword: str, location: str):
    """
    Scrapes Google Maps for business leads (Demonstration).
    """
    try:
        query = f"{keyword} in {location}"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        leads = []
        for result in soup.select('.tF2Cxc, .g'): 
            name_tag = result.select_one('h3')
            link_tag = result.select_one('a')
            website_tag = result.select_one('cite')
            
            if name_tag and link_tag and website_tag:
                name = name_tag.get_text()
                website_url = link_tag['href']
                clean_website = website_tag.get_text().split(' ')[0]
                
                if 'google.com' not in website_url:
                    email = find_email_on_site(clean_website)
                    leads.append({
                        "name": name, "website": clean_website, "email": email, "niche": keyword
                    })
        
        if not leads:
            return {"message": "No results found. Google may be blocking requests.", "leads": []}
            
        return {"leads": leads[:5]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")