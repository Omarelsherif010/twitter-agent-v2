import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from config import HOST, PORT, DEBUG
from database.db import init_db
from auth.routes import auth_router
from twitter.routes import twitter_router

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Agent V2",
    description="A Twitter agent application that uses Tweepy with OAuth 2.0 for multi-user authentication",
    version="0.1.0"
)

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(twitter_router, prefix="/twitter", tags=["Twitter"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint that displays the home page
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup():
    """
    Initialize database on startup
    """
    await init_db()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Run the application
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)
