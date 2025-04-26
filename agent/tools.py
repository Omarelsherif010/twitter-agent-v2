import json
import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable
from smolagents import tool
from twitter.api import TwitterAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_tweet(twitter_api: TwitterAPI, text: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
    """Post a new tweet to Twitter. Use this when the user wants to post content to their Twitter account.
    
    Args:
        twitter_api: The Twitter API client instance.
        text: The text content of the tweet.
        reply_to_id: Optional ID of a tweet to reply to.
        
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        result = await twitter_api.post_tweet(text=text, reply_to_id=reply_to_id)
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
    
async def get_user_timeline(twitter_api: TwitterAPI, limit: int = 10) -> Dict[str, Any]:
    """Get the user's Twitter timeline. Use this when the user wants to see their recent tweets or activity.
    
    Args:
        twitter_api: The Twitter API client instance.
        limit: Maximum number of tweets to retrieve.
        
    Returns:
        A dictionary with the timeline tweets and metadata.
    """
    try:
        tweets = await twitter_api.get_user_timeline(limit=limit)
        
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


async def search_tweets(twitter_api: TwitterAPI, query: str, limit: int = 10) -> Dict[str, Any]:
    """Search for tweets using a keyword or hashtag. Use this when the user wants to find tweets about a specific topic.
    
    Args:
        twitter_api: The Twitter API client instance.
        query: The search query or keyword.
        limit: Maximum number of tweets to retrieve.
        
    Returns:
        A dictionary with the search results and metadata.
    """
    try:
        tweets = await twitter_api.search_tweets(query=query, limit=limit)
        
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


async def get_user_info(twitter_api: TwitterAPI) -> Dict[str, Any]:
    """Get information about the authenticated user. Use this when the user wants to know about their Twitter profile.
    
    Args:
        twitter_api: The Twitter API client instance.
        
    Returns:
        A dictionary with the user's profile information.
    """
    try:
        user_info = await twitter_api.get_user_info()
        
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


async def like_tweet(twitter_api: TwitterAPI, tweet_id: str) -> Dict[str, Any]:
    """Like a tweet on Twitter. Use this when the user wants to like a specific tweet.
    
    Args:
        twitter_api: The Twitter API client instance.
        tweet_id: The ID of the tweet to like.
        
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        result = await twitter_api.like_tweet(tweet_id=tweet_id)
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


async def unlike_tweet(twitter_api: TwitterAPI, tweet_id: str) -> Dict[str, Any]:
    """Unlike a tweet on Twitter. Use this when the user wants to unlike a specific tweet.
    
    Args:
        twitter_api: The Twitter API client instance.
        tweet_id: The ID of the tweet to unlike.
        
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        result = await twitter_api.unlike_tweet(tweet_id=tweet_id)
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


async def follow_user(twitter_api: TwitterAPI, target_user_id: str) -> Dict[str, Any]:
    """Follow a user on Twitter. Use this when the user wants to follow another Twitter user.
    
    Args:
        twitter_api: The Twitter API client instance.
        target_user_id: The ID of the user to follow.
        
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        result = await twitter_api.follow_user(target_user_id=target_user_id)
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


async def unfollow_user(twitter_api: TwitterAPI, target_user_id: str) -> Dict[str, Any]:
    """Unfollow a user on Twitter. Use this when the user wants to unfollow another Twitter user.
    
    Args:
        twitter_api: The Twitter API client instance.
        target_user_id: The ID of the user to unfollow.
        
    Returns:
        A dictionary with the result of the operation.
    """
    try:
        result = await twitter_api.unfollow_user(target_user_id=target_user_id)
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


class TwitterTools:
    """Collection of Twitter API tools for the AI agent."""
    
    def __init__(self, twitter_api: TwitterAPI):
        """
        Initialize TwitterTools with a Twitter API instance.
        
        Args:
            twitter_api: The Twitter API client instance.
        """
        self.twitter_api = twitter_api
        logger.info(f"Initialized TwitterTools for user_id={twitter_api.user_id}, twitter_user_id={twitter_api.twitter_user_id}")
    
    def create_tools(self) -> List[Callable[..., Awaitable[Dict[str, Any]]]]:
        """
        Create and return the list of tools that the agent can use.
        
        Returns:
            List of tool functions that can be used by the agent.
        """
        @tool
        async def post_tweet_tool(text: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
            """
            Post a new tweet to Twitter. Use this when the user wants to post content to their Twitter account.
            
            Args:
                text: The text content of the tweet.
                reply_to_id: Optional ID of a tweet to reply to.
                
            Returns:
                A dictionary with the result of the operation.
            """
            return await post_tweet(self.twitter_api, text, reply_to_id)
        
        @tool
        async def get_timeline_tool(limit: int = 10) -> Dict[str, Any]:
            """
            Get the user's Twitter timeline. Use this when the user wants to see their recent tweets or activity.
            
            Args:
                limit: Maximum number of tweets to retrieve.
                
            Returns:
                A dictionary with the timeline tweets and metadata.
            """
            return await get_user_timeline(self.twitter_api, limit)
        
        @tool
        async def search_tweets_tool(query: str, limit: int = 10) -> Dict[str, Any]:
            """
            Search for tweets using a keyword or hashtag. Use this when the user wants to find tweets about a specific topic.
            
            Args:
                query: The search query or keyword.
                limit: Maximum number of tweets to retrieve.
                
            Returns:
                A dictionary with the search results and metadata.
            """
            return await search_tweets(self.twitter_api, query, limit)
        
        @tool
        async def get_user_info_tool() -> Dict[str, Any]:
            """
            Get information about the authenticated user. Use this when the user wants to know about their Twitter profile.
            
            Returns:
                A dictionary with the user's profile information.
            """
            return await get_user_info(self.twitter_api)
        
        @tool
        async def like_tweet_tool(tweet_id: str) -> Dict[str, Any]:
            """
            Like a tweet on Twitter. Use this when the user wants to like a specific tweet.
            
            Args:
                tweet_id: The ID of the tweet to like.
                
            Returns:
                A dictionary with the result of the operation.
            """
            return await like_tweet(self.twitter_api, tweet_id)
        
        @tool
        async def unlike_tweet_tool(tweet_id: str) -> Dict[str, Any]:
            """
            Unlike a tweet on Twitter. Use this when the user wants to unlike a specific tweet.
            
            Args:
                tweet_id: The ID of the tweet to unlike.
                
            Returns:
                A dictionary with the result of the operation.
            """
            return await unlike_tweet(self.twitter_api, tweet_id)
        
        @tool
        async def follow_user_tool(target_user_id: str) -> Dict[str, Any]:
            """
            Follow a user on Twitter. Use this when the user wants to follow another Twitter user.
            
            Args:
                target_user_id: The ID of the user to follow.
                
            Returns:
                A dictionary with the result of the operation.
            """
            return await follow_user(self.twitter_api, target_user_id)
        
        @tool
        async def unfollow_user_tool(target_user_id: str) -> Dict[str, Any]:
            """
            Unfollow a user on Twitter. Use this when the user wants to unfollow another Twitter user.
            
            Args:
                target_user_id: The ID of the user to unfollow.
                
            Returns:
                A dictionary with the result of the operation.
            """
            return await unfollow_user(self.twitter_api, target_user_id)
        
        # Return the list of tools
        return [
            post_tweet_tool,
            get_timeline_tool,
            search_tweets_tool,
            get_user_info_tool,
            like_tweet_tool,
            unlike_tweet_tool,
            follow_user_tool,
            unfollow_user_tool
        ]
        
    def get_tools(self) -> List[Callable[..., Awaitable[Dict[str, Any]]]]:
        """
        Get all Twitter tools bound to the current Twitter API instance.
        This is a compatibility method that calls create_tools().
        
        Returns:
            List of tool functions that can be used by the agent.
        """
        return self.create_tools()
