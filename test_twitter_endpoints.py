"""
Test script for Twitter API endpoints.

This script directly tests the Twitter API endpoints without using the agent.
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from twitter.api import TwitterAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_twitter_endpoints():
    """Test the Twitter API endpoints directly."""
    # Initialize Twitter API with an authenticated user ID from tokens.json
    user_id = "2"  # Using user_id 2 which is active in tokens.json
    logger.info(f"Initializing TwitterAPI for user_id: {user_id}")
    
    twitter_api = TwitterAPI(user_id=user_id)
    await twitter_api.initialize_client()
    
    # Get username from token data
    if hasattr(twitter_api, 'token') and twitter_api.token:
        username = twitter_api.token.get('twitter_username', 'unknown')
        logger.info(f"Twitter API initialized for user: {username}")
    else:
        logger.info("Twitter API initialized successfully")
    
    # Test getting user timeline
    logger.info("Testing get_user_timeline endpoint...")
    try:
        timeline = await twitter_api.get_user_timeline(limit=5)
        logger.info(f"Successfully retrieved {len(timeline)} tweets from timeline")
        for i, tweet in enumerate(timeline[:3], 1):  # Show first 3 tweets
            logger.info(f"Tweet {i}: {tweet.get('text', '')[:50]}...")
    except Exception as e:
        logger.error(f"Error getting user timeline: {str(e)}")
    
    # Test searching tweets
    search_query = "python"
    logger.info(f"Testing search_tweets endpoint with query: '{search_query}'...")
    try:
        # Twitter API requires minimum 10 results for search
        search_results = await twitter_api.search_tweets(query=search_query, limit=10)
        logger.info(f"Successfully retrieved {len(search_results)} tweets from search")
        for i, tweet in enumerate(search_results[:3], 1):  # Show first 3 tweets
            logger.info(f"Tweet {i}: {tweet.get('text', '')[:50]}...")
    except Exception as e:
        logger.error(f"Error searching tweets: {str(e)}")
    
    # Test getting user info
    logger.info("Testing get_user_info endpoint...")
    try:
        user_info = await twitter_api.get_user_info()
        logger.info(f"Successfully retrieved user info:")
        logger.info(f"  Username: {user_info.get('username', '')}")
        logger.info(f"  Name: {user_info.get('name', '')}")
        logger.info(f"  Followers: {user_info.get('followers_count', 0)}")
        logger.info(f"  Following: {user_info.get('following_count', 0)}")
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
    
    # Test posting a tweet (commented out to avoid accidental tweets)
    """
    logger.info("Testing post_tweet endpoint...")
    try:
        tweet_text = f"Testing Twitter API endpoints directly - {os.urandom(4).hex()}"
        result = await twitter_api.post_tweet(text=tweet_text)
        logger.info(f"Successfully posted tweet: {result.get('text', '')}")
        logger.info(f"Tweet ID: {result.get('id', '')}")
    except Exception as e:
        logger.error(f"Error posting tweet: {str(e)}")
    """
    
    logger.info("Twitter API endpoint tests completed")

if __name__ == "__main__":
    asyncio.run(test_twitter_endpoints())
