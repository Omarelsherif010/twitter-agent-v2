"""
Comprehensive test script for Twitter API endpoints.

This script tests all the major Twitter API endpoints and provides detailed output.
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from twitter.api import TwitterAPI
from agent.utils import save_json, generate_timestamped_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_twitter_endpoints():
    """Test all major Twitter API endpoints comprehensively."""
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
    
    # Dictionary to store all test results
    test_results = {
        "timestamp": generate_timestamped_filename("", ""),
        "user_id": user_id,
        "endpoints": {}
    }
    
    # Test 1: Get user info
    logger.info("\n=== Testing get_user_info endpoint ===")
    try:
        user_info = await twitter_api.get_user_info()
        logger.info(f"Successfully retrieved user info:")
        logger.info(f"  Username: {user_info.get('username', '')}")
        logger.info(f"  Name: {user_info.get('name', '')}")
        logger.info(f"  Followers: {user_info.get('followers_count', 0)}")
        logger.info(f"  Following: {user_info.get('following_count', 0)}")
        
        test_results["endpoints"]["get_user_info"] = {
            "success": True,
            "data": user_info
        }
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        test_results["endpoints"]["get_user_info"] = {
            "success": False,
            "error": str(e)
        }
    
    # Test 2: Get user timeline
    logger.info("\n=== Testing get_user_timeline endpoint ===")
    try:
        timeline = await twitter_api.get_user_timeline(limit=5)
        logger.info(f"Successfully retrieved {len(timeline)} tweets from timeline")
        
        # Display first 3 tweets
        for i, tweet in enumerate(timeline[:3], 1):
            logger.info(f"Tweet {i}:")
            logger.info(f"  ID: {tweet.get('id', '')}")
            logger.info(f"  Text: {tweet.get('text', '')[:100]}...")
            logger.info(f"  Created at: {tweet.get('created_at', '')}")
            logger.info(f"  Likes: {tweet.get('public_metrics', {}).get('like_count', 0)}")
            logger.info(f"  Retweets: {tweet.get('public_metrics', {}).get('retweet_count', 0)}")
        
        test_results["endpoints"]["get_user_timeline"] = {
            "success": True,
            "count": len(timeline),
            "sample": timeline[:3] if timeline else []
        }
    except Exception as e:
        logger.error(f"Error getting user timeline: {str(e)}")
        test_results["endpoints"]["get_user_timeline"] = {
            "success": False,
            "error": str(e)
        }
    
    # Test 3: Search tweets
    logger.info("\n=== Testing search_tweets endpoint ===")
    search_query = "python"
    try:
        # Twitter API requires minimum 10 results for search
        search_results = await twitter_api.search_tweets(query=search_query, limit=10)
        logger.info(f"Successfully retrieved {len(search_results)} tweets from search")
        
        # Display first 3 tweets
        for i, tweet in enumerate(search_results[:3], 1):
            logger.info(f"Tweet {i}:")
            logger.info(f"  ID: {tweet.get('id', '')}")
            logger.info(f"  Text: {tweet.get('text', '')[:100]}...")
            logger.info(f"  Author: {tweet.get('author', {}).get('username', '')}")
            logger.info(f"  Created at: {tweet.get('created_at', '')}")
        
        test_results["endpoints"]["search_tweets"] = {
            "success": True,
            "query": search_query,
            "count": len(search_results),
            "sample": search_results[:3] if search_results else []
        }
    except Exception as e:
        logger.error(f"Error searching tweets: {str(e)}")
        test_results["endpoints"]["search_tweets"] = {
            "success": False,
            "query": search_query,
            "error": str(e)
        }
    
    # Test 4: Post a tweet (commented out to avoid accidental tweets)
    """
    logger.info("\n=== Testing post_tweet endpoint ===")
    try:
        tweet_text = f"Testing Twitter API endpoints - {os.urandom(4).hex()}"
        result = await twitter_api.post_tweet(text=tweet_text)
        logger.info(f"Successfully posted tweet:")
        logger.info(f"  ID: {result.get('id', '')}")
        logger.info(f"  Text: {result.get('text', '')}")
        
        test_results["endpoints"]["post_tweet"] = {
            "success": True,
            "tweet_id": result.get('id', ''),
            "text": result.get('text', '')
        }
        
        # Store the tweet ID for later tests
        tweet_id = result.get('id', '')
    except Exception as e:
        logger.error(f"Error posting tweet: {str(e)}")
        test_results["endpoints"]["post_tweet"] = {
            "success": False,
            "error": str(e)
        }
        tweet_id = None
    """
    
    # Save test results to a JSON file
    results_file = f"twitter_api_test_results_{generate_timestamped_filename('', 'json')}"
    results_path = os.path.join("data", results_file)
    save_json(test_results, results_path)
    logger.info(f"\nTest results saved to {results_path}")
    
    logger.info("\nTwitter API endpoint tests completed")
    return test_results

if __name__ == "__main__":
    asyncio.run(test_twitter_endpoints())
