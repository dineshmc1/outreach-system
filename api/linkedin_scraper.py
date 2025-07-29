from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import urllib.parse

# Use APIRouter
router = APIRouter()

class LinkedinSearchRequest(BaseModel):
    email: str
    password: str
    search_keyword: str
    # Optional: limit the number of pages to scrape to avoid timeouts
    max_pages: int = 2 

@router.post("/linkedin-search")
async def linkedin_search(request: LinkedinSearchRequest):
    """
    Performs a LinkedIn search for people, scrapes the results, and returns them as JSON.
    WARNING: This is a long-running task and may time out on standard hosting plans.
    It is also against LinkedIn's ToS and can result in your account being banned.
    """
    
    # --- Selenium Configuration for Render/Linux ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Must be headless to run on a server
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    scraped_data = []

    try:
        # Use Service to manage the driver
        # The buildpack will place chromedriver in the PATH
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 1. Login to LinkedIn
        driver.get('https://www.linkedin.com/login')
        time.sleep(2) # Allow page to load
        driver.find_element(By.ID, 'username').send_keys(request.email)
        driver.find_element(By.ID, 'password').send_keys(request.password)
        driver.find_element(By.XPATH, "//*[@type='submit']").click()
        time.sleep(5) # Wait for login and potential redirect

        # Check for login failure
        if 'feed' not in driver.current_url:
            raise HTTPException(status_code=401, detail="LinkedIn login failed. Check credentials or for a security challenge.")

        # 2. Perform Search
        keyword_encoded = urllib.parse.quote(request.search_keyword)
        
        print(f"Starting scrape for '{request.search_keyword}' for {request.max_pages} pages.")

        for page_num in range(1, request.max_pages + 1):
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword_encoded}&origin=GLOBAL_SEARCH_HEADER&page={page_num}"
            driver.get(search_url)
            time.sleep(3) # Wait for search results to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # This selector is more robust and finds the container of the search result
            results = soup.find_all('li', class_='reusable-search__result-container')
            
            if not results:
                print(f"No more results found on page {page_num}.")
                break
            
            print(f"Found {len(results)} results on page {page_num}.")

            # Collect profile URLs first to avoid stale element issues
            profile_urls = []
            for result in results:
                profile_link_tag = result.find('a', class_='app-aware-link')
                if profile_link_tag and 'href' in profile_link_tag.attrs:
                    url = profile_link_tag['href']
                    # Ensure it's a profile URL and not something else
                    if "linkedin.com/in/" in url:
                        profile_urls.append(url)
            
            # Visit each profile
            for url in profile_urls:
                driver.get(url)
                time.sleep(3)
                profile_soup = BeautifulSoup(driver.page_source, 'lxml')
                
                # Scrape details (selectors updated for modern LinkedIn)
                try:
                    name = profile_soup.find('h1', class_='text-heading-xlarge').get_text(strip=True)
                except:
                    name = 'N/A'

                try:
                    headline = profile_soup.find('div', class_='text-body-medium').get_text(strip=True)
                except:
                    headline = 'N/A'

                try:
                    location = profile_soup.find('span', class_='text-body-small inline t-black--light break-words').get_text(strip=True)
                except:
                    location = 'N/A'

                scraped_data.append({
                    'profile_url': url,
                    'name': name,
                    'headline': headline,
                    'location': location,
                })
        
        return {"status": "success", "results_count": len(scraped_data), "data": scraped_data}

    except HTTPException as e:
        raise e # Re-raise HTTP exceptions
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during scraping: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()