from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional, List, Dict, Any

from auth.oauth import OAuth2Handler
from database.db import get_users, get_user, get_tokens, update_token_by_user_id

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create router
auth_router = APIRouter()

# Initialize OAuth handler
oauth_handler = OAuth2Handler()

@auth_router.get("/login")
async def login(request: Request):
    """
    Redirect to Twitter OAuth authorization URL or return the URL as JSON
    """
    authorization_url = oauth_handler.get_authorization_url()
    
    # Check if the request accepts JSON
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header:
        return {"authorization_url": authorization_url}
    
    # Otherwise, redirect the browser
    return RedirectResponse(authorization_url)

@auth_router.get("/callback")
async def callback(request: Request, code: str, state: Optional[str] = None):
    """
    Handle OAuth callback from Twitter
    """
    try:
        # Get the full callback URL including query parameters
        callback_url = str(request.url)
        
        # Exchange code for token using the full callback URL
        token_data = await oauth_handler.fetch_token(callback_url)
        
        # Save token to database
        user, token = await oauth_handler.save_token(token_data)
        
        # Return success page
        return templates.TemplateResponse(
            "auth_success.html", 
            {
                "request": request, 
                "username": token["twitter_username"]
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "auth_error.html", 
            {
                "request": request, 
                "error": str(e)
            }
        )

@auth_router.get("/users")
async def get_all_users():
    """
    Get all authenticated users
    """
    users_data = await get_users()
    tokens_data = await get_tokens()
    
    # Combine user and token data
    result = []
    for user_id, user in users_data.items():
        # Find the token for this user
        user_token = None
        for token_id, token in tokens_data.items():
            if token.get("user_id") == user_id:
                user_token = token
                break
        
        if user_token:
            result.append({
                "id": user_id,
                "username": user.get("username"),
                "twitter_username": user_token.get("twitter_username"),
                "is_active": user_token.get("is_active", True)
            })
    
    return {"users": result}

@auth_router.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    """
    Get a specific user by ID
    """
    user_data = await get_user(user_id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get tokens data to find the token for this user
    tokens_data = await get_tokens()
    user_token = None
    
    for token_id, token in tokens_data.items():
        if token.get("user_id") == user_id:
            user_token = token
            break
    
    if not user_token:
        raise HTTPException(status_code=404, detail="User token not found")
    
    # Combine user and token data
    result = {
        "id": user_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "created_at": user_data.get("created_at"),
        "twitter_username": user_token.get("twitter_username"),
        "twitter_user_id": user_token.get("twitter_user_id"),
        "is_active": user_token.get("is_active", True),
        "scopes": user_token.get("scopes", "")
    }
    
    return {"user": result}

@auth_router.post("/revoke/{user_id}")
async def revoke_access(user_id: str):
    """
    Revoke a user's Twitter access
    """
    # Update token to set is_active to False
    result = await update_token_by_user_id(user_id, {"is_active": False})
    
    if not result:
        raise HTTPException(status_code=404, detail="User token not found")
    
    return {"message": "Access revoked successfully"}
