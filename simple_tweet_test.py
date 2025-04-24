import asyncio
import json
from twitter.api import TwitterAPI
from database.db import get_tokens

async def main():
    """
    Simple script to test Twitter operations
    """
    # Get the first active token
    tokens = await get_tokens()
    active_token = None
    
    for token_id, token in tokens.items():
        if token.get("is_active", False):
            active_token = token
            break
    
    if not active_token:
        print("No active tokens found. Please authenticate first.")
        return
    
    twitter_user_id = active_token["twitter_user_id"]
    print(f"Using Twitter account: @{active_token['twitter_username']}")
    
    # Initialize Twitter API
    api = TwitterAPI(twitter_user_id=twitter_user_id)
    
    # 1. Post a tweet
    tweet_text = "Hello from Twitter Agent V2! This is a test tweet posted at " + \
                 asyncio.get_event_loop().time().__str__()
    
    print(f"\nPosting tweet: {tweet_text}")
    try:
        tweet_result = await api.post_tweet(text=tweet_text)
        print(f"Tweet posted successfully!")
        print(f"Tweet ID: {tweet_result.get('id')}")
        print(f"Tweet text: {tweet_result.get('text')}")
    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
    
    # 2. Get user info
    print("\nFetching user info...")
    try:
        user_info = await api.get_user_info()
        print(json.dumps(user_info, indent=2, default=str))
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
    
    # 3. Get timeline
    print("\nFetching timeline (5 tweets)...")
    try:
        timeline = await api.get_user_timeline(limit=5)
        
        if not timeline:
            print("No tweets found in timeline.")
        else:
            for i, tweet in enumerate(timeline, 1):
                print(f"\n{i}. Tweet ID: {tweet.get('id')}")
                print(f"   Text: {tweet.get('text')}")
                print(f"   Created at: {tweet.get('created_at', 'Unknown')}")
                if 'author_id' in tweet:
                    print(f"   Author ID: {tweet.get('author_id')}")
    except Exception as e:
        print(f"Error fetching timeline: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
