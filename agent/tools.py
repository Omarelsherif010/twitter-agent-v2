from typing import List, Optional, Dict, Any
from smolagents import Tool, tool
from twitter.api import TwitterAPI

@tool
async def post_tweet(twitter_api: TwitterAPI, text: str, reply_to_id: Optional[str] = None) -> str:
    """Post a new tweet to Twitter. Use this when the user wants to post content to their Twitter account.
    
    Args:
        twitter_api: The Twitter API client instance.
        text: The text content of the tweet.
        reply_to_id: Optional ID of a tweet to reply to.
        
    Returns:
        A message indicating the tweet was posted successfully or an error message.
    """
    try:
        result = await twitter_api.post_tweet(text=text, reply_to_id=reply_to_id)
        return f"Tweet posted successfully! Tweet ID: {result.get('id', '')}"
    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        return f"Failed to post tweet: {str(e)}"
    
@tool
async def get_user_timeline(twitter_api: TwitterAPI, limit: int = 10) -> str:
    """Get the user's Twitter timeline. Use this when the user wants to see their recent tweets or activity.
    
    Args:
        twitter_api: The Twitter API client instance.
        limit: Maximum number of tweets to retrieve.
        
    Returns:
        A formatted string containing the user's timeline tweets.
    """
    try:
        tweets = await twitter_api.get_user_timeline(limit=limit)
        if not tweets:
            return "No tweets found in your timeline."
            
        result = f"Retrieved {len(tweets)} tweets from your timeline:\n\n"
        for i, tweet in enumerate(tweets, 1):
            author = tweet.get("author", {}).get("username", "Unknown")
            text = tweet.get("text", "")
            created_at = tweet.get("created_at", "")
            result += f"{i}. @{author}: {text}\n   Posted on: {created_at}\n\n"
        return result
    except Exception as e:
        print(f"Error getting timeline: {str(e)}")
        return f"Failed to get timeline: {str(e)}"


@tool
async def search_tweets(twitter_api: TwitterAPI, query: str, limit: int = 10) -> str:
    """Search for tweets using a keyword or hashtag. Use this when the user wants to find tweets about a specific topic.
    
    Args:
        twitter_api: The Twitter API client instance.
        query: The search query or keyword.
        limit: Maximum number of tweets to retrieve.
        
    Returns:
        A formatted string containing the search results.
    """
    try:
        tweets = await twitter_api.search_tweets(query=query, limit=limit)
        if not tweets:
            return f"No tweets found matching '{query}'."
            
        result = f"Found {len(tweets)} tweets matching '{query}':\n\n"
        for i, tweet in enumerate(tweets, 1):
            author = tweet.get("author", {}).get("username", "Unknown")
            text = tweet.get("text", "")
            created_at = tweet.get("created_at", "")
            result += f"{i}. @{author}: {text}\n   Posted on: {created_at}\n\n"
        return result
    except Exception as e:
        print(f"Error searching tweets: {str(e)}")
        return f"Failed to search tweets: {str(e)}"


@tool
async def get_user_info(twitter_api: TwitterAPI) -> str:
    """Get information about the authenticated user. Use this when the user wants to know about their Twitter profile.
    
    Args:
        twitter_api: The Twitter API client instance.
        
    Returns:
        A formatted string containing the user's profile information.
    """
    try:
        user_info = await twitter_api.get_user_info()
        username = user_info.get("username", "Unknown")
        name = user_info.get("name", "Unknown")
        user_id = user_info.get("id", "Unknown")
        followers = user_info.get("public_metrics", {}).get("followers_count", 0)
        following = user_info.get("public_metrics", {}).get("following_count", 0)
        tweet_count = user_info.get("public_metrics", {}).get("tweet_count", 0)
        description = user_info.get("description", "No description")
        
        result = f"Profile information for @{username}:\n\n"
        result += f"Name: {name}\n"
        result += f"User ID: {user_id}\n"
        result += f"Followers: {followers}\n"
        result += f"Following: {following}\n"
        result += f"Tweet count: {tweet_count}\n"
        result += f"Description: {description}\n"
        
        return result
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return f"Failed to get user info: {str(e)}"


class TwitterTools:
    """Collection of Twitter API tools for the AI agent."""
    
    def __init__(self, twitter_api: TwitterAPI):
        self.twitter_api = twitter_api
        
    def get_tools(self) -> List[Any]:
        """Get all Twitter tools."""
        # Create bound functions that pass the twitter_api instance as the first parameter
        async def post_tweet_tool(text: str, reply_to_id: Optional[str] = None) -> str:
            """Post a new tweet to Twitter. Use this when the user wants to post content to their Twitter account.
            
            Args:
                text: The text content of the tweet.
                reply_to_id: Optional ID of a tweet to reply to.
                
            Returns:
                A message indicating the tweet was posted successfully or an error message.
            """
            return await post_tweet(self.twitter_api, text, reply_to_id)
            
        async def get_timeline_tool(limit: int = 10) -> str:
            """Get the user's Twitter timeline. Use this when the user wants to see their recent tweets or activity.
            
            Args:
                limit: Maximum number of tweets to retrieve.
                
            Returns:
                A formatted string containing the user's timeline tweets.
            """
            return await get_user_timeline(self.twitter_api, limit)
            
        async def search_tweets_tool(query: str, limit: int = 10) -> str:
            """Search for tweets using a keyword or hashtag. Use this when the user wants to find tweets about a specific topic.
            
            Args:
                query: The search query or keyword.
                limit: Maximum number of tweets to retrieve.
                
            Returns:
                A formatted string containing the search results.
            """
            return await search_tweets(self.twitter_api, query, limit)
            
        async def get_user_info_tool() -> str:
            """Get information about the authenticated user. Use this when the user wants to know about their Twitter profile.
            
            Returns:
                A formatted string containing the user's profile information.
            """
            return await get_user_info(self.twitter_api)
        
        # Return the tool functions
        return [
            post_tweet_tool,
            get_timeline_tool,
            search_tweets_tool,
            get_user_info_tool
        ]
