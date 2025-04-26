import uvicorn
from fastapi import FastAPI
import os

from config import HOST, PORT, DEBUG
from database.db import init_db
from auth.routes import auth_router
from twitter.routes import twitter_router
from agent.routes import agent_router

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Agent V2",
    description="A Twitter agent application that uses Tweepy with OAuth 2.0 for multi-user authentication",
    version="0.1.0"
)

# Include routers
app.include_router(auth_router, prefix="/oauth", tags=["Authentication"])
app.include_router(twitter_router, prefix="/twitter", tags=["Twitter"])
app.include_router(agent_router, prefix="/agent", tags=["Agent"])

@app.get("/")
async def root():
    """
    Root endpoint that returns API information
    """
    return {
        "name": "Twitter Agent V2 API",
        "version": "0.1.0",
        "description": "Twitter agent API with OAuth 2.0 authentication",
        "endpoints": [
            "/oauth/login",
            "/twitter/tweet",
            "/twitter/timeline",
            "/twitter/search",
            "/twitter/agent"
        ]
    }

@app.on_event("startup")
async def startup():
    """
    Initialize database on startup
    """
    await init_db()

if __name__ == "__main__":
    # Ensure data directory exists for JSON storage
    os.makedirs("data", exist_ok=True)
    
    # Run the application
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)
