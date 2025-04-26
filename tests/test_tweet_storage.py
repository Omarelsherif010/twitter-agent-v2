import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import save_tweets, get_saved_tweets

async def test_tweet_storage():
    """Test the tweet storage functionality"""
    print("Testing tweet storage functionality...")
    
    # Create test tweets
    test_tweets = [
        {
            "id": "1234567890",
            "text": "This is a test tweet for storage",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "0987654321",
            "text": "Another test tweet for storage",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    # Test user ID
    user_id = "3"
    
    # Save tweets with different types
    print(f"Saving timeline tweets for user {user_id}...")
    await save_tweets(user_id, test_tweets, tweet_type="timeline")
    
    print(f"Saving search tweets for user {user_id}...")
    await save_tweets(user_id, test_tweets, tweet_type="search_test")
    
    print(f"Saving posted tweets for user {user_id}...")
    await save_tweets(user_id, test_tweets, tweet_type="posted")
    
    # Retrieve saved tweets
    print(f"Retrieving all saved tweets for user {user_id}...")
    all_tweets = await get_saved_tweets(user_id)
    print(f"Found {len(all_tweets)} tweet files")
    
    # Retrieve timeline tweets
    print(f"Retrieving timeline tweets for user {user_id}...")
    timeline_tweets = await get_saved_tweets(user_id, tweet_type="timeline")
    print(f"Found {len(timeline_tweets)} timeline tweet files")
    
    # Retrieve search tweets
    print(f"Retrieving search tweets for user {user_id}...")
    search_tweets = await get_saved_tweets(user_id, tweet_type="search_test")
    print(f"Found {len(search_tweets)} search tweet files")
    
    # Retrieve posted tweets
    print(f"Retrieving posted tweets for user {user_id}...")
    posted_tweets = await get_saved_tweets(user_id, tweet_type="posted")
    print(f"Found {len(posted_tweets)} posted tweet files")
    
    # Print the directory structure
    tweets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tweets')
    print(f"\nTweet storage directory structure:")
    for root, dirs, files in os.walk(tweets_dir):
        level = root.replace(tweets_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")

if __name__ == "__main__":
    asyncio.run(test_tweet_storage())
