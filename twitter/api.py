import tweepy
from fastapi import HTTPException
import datetime
from typing import Dict, List, Optional, Any

from config import TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
from database.db import get_token_by_user_id, get_token_by_twitter_user_id, update_token
from twitter.utils import serialize_datetime, serialize_tweet_data

class TwitterAPI:
    """
    Wrapper for Twitter API operations using Tweepy
    """
    def __init__(self, user_id: int = None, twitter_user_id: str = None):
        """
        Initialize the Twitter API wrapper with either user_id or twitter_user_id
        """
        self.client_id = TWITTER_CLIENT_ID
        self.client_secret = TWITTER_CLIENT_SECRET
        self.user_id = user_id
        self.twitter_user_id = twitter_user_id
        self.client = None
    
    async def initialize_client(self) -> None:
        """
        Initialize the Tweepy client with the user's access token
        """
        # Get token from database
        token = await self._get_token()
        
        if not token:
            raise HTTPException(status_code=404, detail="User not found or not authenticated with Twitter")
        
        # Check if token is expired and refresh if needed
        # Parse the expires_at string to datetime if it's a string
        expires_at = token["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.datetime.fromisoformat(expires_at)
            
        if expires_at < datetime.datetime.utcnow():
            await self._refresh_token(token)
            # Get updated token
            token = await self._get_token()
        
        # Initialize Tweepy client with OAuth 2.0 User Context
        # For OAuth 2.0, we use the access token as the bearer token
        # Important: We must set user_auth=False when using OAuth 2.0 bearer tokens
        self.client = tweepy.Client(
            bearer_token=token["access_token"],
            consumer_key=None,
            consumer_secret=None,
            access_token=None,
            access_token_secret=None
        )
        
        # Store token data
        self.token = token
    
    async def _get_token(self) -> Optional[Dict[str, Any]]:
        """
        Get the user's token from the JSON storage
        """
        if self.user_id:
            return await get_token_by_user_id(self.user_id)
        elif self.twitter_user_id:
            return await get_token_by_twitter_user_id(self.twitter_user_id)
        
        return None
    
    async def _refresh_token(self, token: Dict[str, Any]) -> None:
        """
        Refresh an expired access token
        """
        from auth.oauth import OAuth2Handler
        
        oauth_handler = OAuth2Handler()
        
        try:
            # Refresh the token
            new_token_data = await oauth_handler.refresh_token(token["refresh_token"])
            
            # Update token in JSON storage
            token_update = {
                "access_token": new_token_data["access_token"],
                "refresh_token": new_token_data.get("refresh_token", token["refresh_token"]),
                "expires_at": new_token_data["expires_at"],
                "updated_at": datetime.datetime.utcnow()
            }
            
            await update_token(token["id"], token_update)
        except Exception as e:
            # Mark token as inactive if refresh fails
            await update_token(token["id"], {"is_active": False})
            raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}")
    
    async def get_user_info(self) -> Dict:
        """
        Get information about the authenticated user
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            # Important: We must set user_auth=False when using OAuth 2.0 bearer tokens
            user_info = self.client.get_me(user_auth=False)
            # Create a serializable dictionary
            result = {
                "id": user_info.data.id,
                "username": user_info.data.username,
                "name": user_info.data.name,
                "profile_image_url": getattr(user_info.data, "profile_image_url", None),
                "verified": getattr(user_info.data, "verified", False)
            }
            
            # Handle created_at separately to ensure proper serialization
            created_at = getattr(user_info.data, "created_at", None)
            result["created_at"] = serialize_datetime(created_at)
            
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user info: {str(e)}")
    
    async def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Dict:
        """
        Post a new tweet
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            # According to the Tweepy docs, we need to use create_tweet method
            # with the text parameter and optionally in_reply_to_tweet_id
            # Important: We must set user_auth=False when using OAuth 2.0 bearer tokens
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id,
                user_auth=False
            )
            
            # The response contains a data attribute with the tweet info
            return {
                "id": response.data["id"],
                "text": response.data["text"]
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to post tweet: {str(e)}")
    
    async def get_tweet(self, tweet_id: str) -> Dict:
        """
        Get a specific tweet by ID
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.get_tweet(id=tweet_id, user_auth=False)
            
            return {
                "id": response.data.id,
                "text": response.data.text,
                "created_at": getattr(response.data, "created_at", None)
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get tweet: {str(e)}")
    
    async def like_tweet(self, tweet_id: str) -> Dict:
        """
        Like a tweet
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.like(tweet_id, user_auth=False)
            return {"success": True, "tweet_id": tweet_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to like tweet: {str(e)}")
    
    async def unlike_tweet(self, tweet_id: str) -> Dict:
        """
        Unlike a tweet
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.unlike(tweet_id, user_auth=False)
            return {"success": True, "tweet_id": tweet_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to unlike tweet: {str(e)}")
    
    async def follow_user(self, target_user_id: str) -> Dict:
        """
        Follow a user
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.follow_user(target_user_id, user_auth=False)
            return {"success": True, "target_user_id": target_user_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to follow user: {str(e)}")
    
    async def unfollow_user(self, target_user_id: str) -> Dict:
        """
        Unfollow a user
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.unfollow_user(target_user_id, user_auth=False)
            return {"success": True, "target_user_id": target_user_id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to unfollow user: {str(e)}")
    
    async def get_user_timeline(self, limit: int = 10) -> List[Dict]:
        """
        Get the user's timeline
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            # Include additional tweet fields to get more information
            # Important: We must set user_auth=False when using OAuth 2.0 bearer tokens
            response = self.client.get_home_timeline(
                max_results=limit,
                tweet_fields=["created_at", "author_id", "conversation_id"],
                user_auth=False
            )
            
            # Check if we have data in the response
            if not hasattr(response, "data") or not response.data:
                return []
                
            tweets = []
            for tweet in response.data:
                # Use the utility function to serialize tweet data
                tweets.append(serialize_tweet_data(tweet))
            
            return tweets
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get timeline: {str(e)}")
    
    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tweets
        """
        if not self.client:
            await self.initialize_client()
        
        try:
            response = self.client.search_recent_tweets(query=query, max_results=limit, user_auth=False)
            
            tweets = []
            for tweet in response.data:
                # Use the utility function to serialize tweet data
                tweets.append(serialize_tweet_data(tweet))
            
            return tweets
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to search tweets: {str(e)}")
