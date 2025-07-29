import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import the routers from your individual API files
from api.generate_email import router as generate_email_router
from api.generate_followup import router as generate_followup_router
from api.generate_sequence import router as generate_sequence_router
from api.email_verifier import router as email_verifier_router
from api.maps_scraper import router as maps_scraper_router
from api.linkedin_scraper import router as linkedin_scraper_router

# Create the main FastAPI application
app = FastAPI(title="OutreachGPT Pro")

# Add CORS Middleware to allow the frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- API Routers ---
# Include all the API endpoints from your other files
app.include_router(generate_email_router, prefix="/api")
app.include_router(generate_followup_router, prefix="/api")
app.include_router(generate_sequence_router, prefix="/api")
app.include_router(email_verifier_router, prefix="/api")
app.include_router(maps_scraper_router, prefix="/api")
app.include_router(linkedin_scraper_router, prefix="/api")

# --- Frontend Serving ---
# This line tells FastAPI to serve your frontend files (index.html, etc.)
# It should be placed at the end
app.mount("/", StaticFiles(directory="public", html=True), name="static")