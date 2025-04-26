import logging
from typing import Dict, List, Optional, Any

from tests.mock_api import MockTwitterAPI

logger = logging.getLogger(__name__)

class MockTwitterTools:
    """Collection of mock Twitter API tools for testing."""
    
    def __init__(self, twitter_api: MockTwitterAPI):
        """
        Initialize MockTwitterTools with a Twitter API instance.
        
        Args:
            twitter_api: The Twitter API client instance.
        """
        self.twitter_api = twitter_api
        logger.info(f"Initialized MockTwitterTools for user_id={twitter_api.user_id}, twitter_user_id={twitter_api.twitter_user_id}")
    
    async def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Post a new tweet to Twitter."""
        try:
            result = await self.twitter_api.post_tweet(text=text, reply_to_id=reply_to_id)
            return {
                "success": True,
                "message": f"Tweet posted successfully! Tweet ID: {result.get('id', '')}",
                "tweet_id": result.get('id', ''),
                "text": result.get('text', '')
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to post tweet: {str(e)}"
            }
    
    async def get_user_timeline(self, limit: int = 10) -> Dict[str, Any]:
        """Get the user's Twitter timeline."""
        try:
            tweets = await self.twitter_api.get_user_timeline(limit=limit)
            
            if not tweets:
                return {
                    "success": True,
                    "message": "No tweets found in your timeline.",
                    "tweets": []
                }
                
            formatted_tweets = []
            for tweet in tweets:
                formatted_tweets.append({
                    "id": tweet.get("id", ""),
                    "text": tweet.get("text", ""),
                    "author": tweet.get("author", {}).get("username", "Unknown"),
                    "created_at": tweet.get("created_at", "")
                })
                
            return {
                "success": True,
                "message": f"Retrieved {len(tweets)} tweets from your timeline.",
                "tweets": formatted_tweets
            }
        except Exception as e:
            logger.error(f"Error getting timeline: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get timeline: {str(e)}"
            }
    
    async def search_tweets(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for tweets using a keyword or hashtag."""
        try:
            tweets = await self.twitter_api.search_tweets(query=query, limit=limit)
            
            if not tweets:
                return {
                    "success": True,
                    "message": f"No tweets found matching '{query}'.",
                    "tweets": []
                }
                
            formatted_tweets = []
            for tweet in tweets:
                formatted_tweets.append({
                    "id": tweet.get("id", ""),
                    "text": tweet.get("text", ""),
                    "author": tweet.get("author", {}).get("username", "Unknown"),
                    "created_at": tweet.get("created_at", "")
                })
                
            return {
                "success": True,
                "message": f"Found {len(tweets)} tweets matching '{query}'.",
                "tweets": formatted_tweets
            }
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to search tweets: {str(e)}"
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get information about the authenticated user."""
        try:
            user_info = await self.twitter_api.get_user_info()
            
            return {
                "success": True,
                "user_info": {
                    "username": user_info.get("username", "Unknown"),
                    "name": user_info.get("name", "Unknown"),
                    "id": user_info.get("id", "Unknown"),
                    "followers_count": user_info.get("public_metrics", {}).get("followers_count", 0),
                    "following_count": user_info.get("public_metrics", {}).get("following_count", 0),
                    "tweet_count": user_info.get("public_metrics", {}).get("tweet_count", 0),
                    "description": user_info.get("description", "No description")
                }
            }
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get user info: {str(e)}"
            }
    
    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet on Twitter."""
        try:
            result = await self.twitter_api.like_tweet(tweet_id=tweet_id)
            return {
                "success": True,
                "message": f"Successfully liked tweet {tweet_id}",
                "tweet_id": tweet_id
            }
        except Exception as e:
            logger.error(f"Error liking tweet: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to like tweet: {str(e)}"
            }
    
    async def unlike_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Unlike a tweet on Twitter."""
        try:
            result = await self.twitter_api.unlike_tweet(tweet_id=tweet_id)
            return {
                "success": True,
                "message": f"Successfully unliked tweet {tweet_id}",
                "tweet_id": tweet_id
            }
        except Exception as e:
            logger.error(f"Error unliking tweet: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to unlike tweet: {str(e)}"
            }
    
    async def follow_user(self, target_user_id: str) -> Dict[str, Any]:
        """Follow a user on Twitter."""
        try:
            result = await self.twitter_api.follow_user(target_user_id=target_user_id)
            return {
                "success": True,
                "message": f"Successfully followed user {target_user_id}",
                "target_user_id": target_user_id
            }
        except Exception as e:
            logger.error(f"Error following user: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to follow user: {str(e)}"
            }
    
    async def unfollow_user(self, target_user_id: str) -> Dict[str, Any]:
        """Unfollow a user on Twitter."""
        try:
            result = await self.twitter_api.unfollow_user(target_user_id=target_user_id)
            return {
                "success": True,
                "message": f"Successfully unfollowed user {target_user_id}",
                "target_user_id": target_user_id
            }
        except Exception as e:
            logger.error(f"Error unfollowing user: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to unfollow user: {str(e)}"
            }
    
    def get_tools(self):
        """Get all mock Twitter tools."""
        return [
            self.post_tweet,
            self.get_user_timeline,
            self.search_tweets,
            self.get_user_info,
            self.like_tweet,
            self.unlike_tweet,
            self.follow_user,
            self.unfollow_user
        ]
