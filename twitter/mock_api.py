import datetime
import logging
import random
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MockTwitterAPI:
    """
    Mock implementation of Twitter API for testing purposes
    """
    def __init__(self, user_id: int = None, twitter_user_id: str = None):
        """
        Initialize the Mock Twitter API wrapper
        """
        self.user_id = user_id
        self.twitter_user_id = twitter_user_id or "1171863380891770882"  # Default mock Twitter ID
        self.client = None
        self.token = {"access_token": "mock_access_token", "refresh_token": "mock_refresh_token"}
        
        # Mock data storage
        self.mock_user_info = {
            "id": self.twitter_user_id,
            "username": "mock_user",
            "name": "Mock User",
            "description": "This is a mock Twitter user for testing purposes",
            "public_metrics": {
                "followers_count": 1000,
                "following_count": 500,
                "tweet_count": 1500
            },
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.mock_tweets = [
            {
                "id": f"tweet_{i}",
                "text": f"This is mock tweet #{i}. #testing #mock",
                "author": {"username": "mock_user", "id": self.twitter_user_id},
                "created_at": (datetime.datetime.now() - datetime.timedelta(days=i)).isoformat()
            }
            for i in range(1, 21)  # Generate 20 mock tweets
        ]
        
        self.mock_timeline = self.mock_tweets[:10]  # First 10 tweets as timeline
        
        # Track liked tweets and followed users
        self.liked_tweets = set()
        self.followed_users = set()
        
        logger.info(f"Initialized MockTwitterAPI for user_id={user_id}, twitter_user_id={twitter_user_id}")
    
    async def initialize_client(self) -> None:
        """
        Mock initialization of client
        """
        logger.info("Mock Twitter client initialized")
        self.client = "mock_client"
    
    async def get_user_info(self) -> Dict:
        """
        Get mock information about the authenticated user
        """
        logger.info("Getting mock user info")
        return self.mock_user_info
    
    async def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Dict:
        """
        Post a mock new tweet
        """
        logger.info(f"Posting mock tweet: {text}")
        
        # Create a new mock tweet
        tweet_id = f"tweet_{str(uuid.uuid4())[:8]}"
        new_tweet = {
            "id": tweet_id,
            "text": text,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        if reply_to_id:
            new_tweet["in_reply_to_id"] = reply_to_id
            
        # Add to mock tweets
        self.mock_tweets.insert(0, new_tweet)
        self.mock_timeline.insert(0, new_tweet)
        
        # Keep timeline at 10 tweets
        if len(self.mock_timeline) > 10:
            self.mock_timeline.pop()
            
        return {
            "id": tweet_id,
            "text": text
        }
    
    async def get_tweet(self, tweet_id: str) -> Dict:
        """
        Get a specific mock tweet by ID
        """
        logger.info(f"Getting mock tweet: {tweet_id}")
        
        # Find the tweet in mock tweets
        for tweet in self.mock_tweets:
            if tweet["id"] == tweet_id:
                return tweet
                
        # If not found, create a mock tweet
        return {
            "id": tweet_id,
            "text": f"This is a mock tweet with ID {tweet_id}",
            "created_at": datetime.datetime.now().isoformat()
        }
    
    async def like_tweet(self, tweet_id: str) -> Dict:
        """
        Like a mock tweet
        """
        logger.info(f"Liking mock tweet: {tweet_id}")
        self.liked_tweets.add(tweet_id)
        return {"success": True, "tweet_id": tweet_id}
    
    async def unlike_tweet(self, tweet_id: str) -> Dict:
        """
        Unlike a mock tweet
        """
        logger.info(f"Unliking mock tweet: {tweet_id}")
        if tweet_id in self.liked_tweets:
            self.liked_tweets.remove(tweet_id)
        return {"success": True, "tweet_id": tweet_id}
    
    async def follow_user(self, target_user_id: str) -> Dict:
        """
        Follow a mock user
        """
        logger.info(f"Following mock user: {target_user_id}")
        self.followed_users.add(target_user_id)
        return {"success": True, "target_user_id": target_user_id}
    
    async def unfollow_user(self, target_user_id: str) -> Dict:
        """
        Unfollow a mock user
        """
        logger.info(f"Unfollowing mock user: {target_user_id}")
        if target_user_id in self.followed_users:
            self.followed_users.remove(target_user_id)
        return {"success": True, "target_user_id": target_user_id}
    
    async def get_user_timeline(self, limit: int = 10) -> List[Dict]:
        """
        Get the mock user's timeline
        """
        logger.info(f"Getting mock timeline with limit: {limit}")
        return self.mock_timeline[:limit]
    
    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for mock tweets
        """
        logger.info(f"Searching mock tweets with query: {query}")
        
        # Filter tweets that contain the query
        matching_tweets = []
        for tweet in self.mock_tweets:
            if query.lower() in tweet["text"].lower():
                matching_tweets.append(tweet)
                if len(matching_tweets) >= limit:
                    break
        
        # If no matches, generate some mock results
        if not matching_tweets:
            matching_tweets = [
                {
                    "id": f"search_{i}_{str(uuid.uuid4())[:8]}",
                    "text": f"This is a mock search result for '{query}'. #{query.replace(' ', '')} #testing",
                    "author": {"username": f"user_{i}", "id": f"user_id_{i}"},
                    "created_at": datetime.datetime.now().isoformat()
                }
                for i in range(1, min(limit + 1, 6))  # Generate up to 'limit' mock search results
            ]
            
        return matching_tweets
