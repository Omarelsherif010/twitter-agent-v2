import tweepy
from fastapi import HTTPException
from datetime import datetime, timedelta
import os
import json
import base64
import hashlib
import urllib.parse
from typing import Dict, Optional, Tuple, Any

from config import TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET, TWITTER_CALLBACK_URL, TWITTER_SCOPES, DEBUG
from database.db import get_token_by_twitter_user_id, create_user, create_token, update_token, get_user
from database.models import User, TwitterToken

# For development only - disable HTTPS requirement
# WARNING: This should NEVER be used in production
if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class OAuth2Handler:
    """
    Handler for Twitter OAuth 2.0 authentication with PKCE
    """
    def __init__(self):
        # Hardcode the values directly to ensure consistency
        self.client_id = "NkNaZGFqeF91NDZBQlpqRFhrV1k6MTpjaQ"  # Hardcoded from .env
        self.client_secret = "-_9G0PyCNVj43aBQYcNPIQHcziQePBylL1dTa0u78bBT9dNNFZ"  # Hardcoded from .env
        self.redirect_uri = "http://localhost:8000/oauth/callback"  # Hardcoded
        self.scopes = ["tweet.read", "tweet.write", "users.read", "follows.read", 
                      "follows.write", "like.read", "like.write", "offline.access"]
        
        # Print the values for debugging
        print(f"DEBUG - Client ID: {self.client_id}")
        print(f"DEBUG - Callback URL: {self.redirect_uri}")
        print(f"DEBUG - Scopes: {self.scopes}")
        
        # Initialize OAuth 2.0 handler with hardcoded values
        self.oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scopes,
            client_secret=self.client_secret
        )
    
    def get_authorization_url(self) -> str:
        """
        Get the authorization URL for Twitter OAuth 2.0
        """
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=500, 
                detail="Twitter API credentials not configured. Please set TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET."
            )
        
        # Let Tweepy handle the PKCE flow
        auth_url = self.oauth2_handler.get_authorization_url()
        
        print("DEBUG - Authorization URL:")
        print(auth_url)
        
        return auth_url
    
    async def fetch_token(self, authorization_response: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_response: The full callback URL with query parameters
        """
        try:
            # Let Tweepy handle the token exchange
            print("DEBUG - Exchanging code for token")
            token_data = self.oauth2_handler.fetch_token(authorization_response)
            
            # Create client with the access token
            # For OAuth 2.0 User Context, we should use the access token as the bearer token
            client = tweepy.Client(
                bearer_token=token_data['access_token']
            )
            
            # Get user information
            user_info = client.get_me(user_auth=False)
            twitter_user_id = user_info.data.id
            twitter_username = user_info.data.username
            
            # Calculate token expiration
            expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            
            return {
                "access_token": token_data['access_token'],
                "refresh_token": token_data.get('refresh_token'),
                "expires_at": expires_at,  # The DateTimeEncoder will handle this
                "twitter_user_id": str(twitter_user_id),
                "twitter_username": twitter_username,
                "scopes": ",".join(token_data.get('scope', []))
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch token: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token
        """
        try:
            # Refresh the token
            token_data = self.oauth2_handler.refresh_token(refresh_token)
            
            # Calculate new expiration
            expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            
            return {
                "access_token": token_data['access_token'],
                "refresh_token": token_data.get('refresh_token', refresh_token),
                "expires_at": expires_at,  # The DateTimeEncoder will handle this
                "scopes": ",".join(token_data.get('scope', []))
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to refresh token: {str(e)}")
    
    async def save_token(self, token_data: Dict[str, Any], user_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Save or update token in the JSON storage
        """
        # Check if a user with this Twitter ID already exists
        existing_token = await get_token_by_twitter_user_id(token_data["twitter_user_id"])
        
        if existing_token:
            # Update existing token
            token_update = {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", existing_token.get("refresh_token")),
                "expires_at": token_data["expires_at"],
                "scopes": token_data.get("scopes", existing_token.get("scopes", "")),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
            
            await update_token(existing_token["id"], token_update)
            
            # Get the user
            user = await get_user(existing_token["user_id"])
            
            # Update the token with new values
            updated_token = {**existing_token, **token_update}
            
            return user, updated_token
        else:
            # Create new user if user_id is not provided
            if not user_id:
                # Create user model
                user_data = {
                    "username": token_data["twitter_username"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Create user in storage
                user_id = await create_user(user_data)
                user_data["id"] = user_id
            else:
                # Get existing user
                user_data = await get_user(user_id)
            
            # Create token model
            token_data_to_save = {
                "user_id": user_id,
                "twitter_user_id": token_data["twitter_user_id"],
                "twitter_username": token_data["twitter_username"],
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data["expires_at"],
                "scopes": token_data.get("scopes", ""),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
            
            # Create token in storage
            token_id = await create_token(token_data_to_save)
            token_data_to_save["id"] = token_id
            
            return user_data, token_data_to_save

