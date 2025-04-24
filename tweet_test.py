import asyncio
import json
import traceback
from twitter.api import TwitterAPI
from database.db import get_tokens

async def main():
    """
    Simple script to test posting a tweet
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
    
    # Post a tweet
    tweet_text = "Hello from Twitter Agent V2! Testing OAuth 2.0 API."
    
    print(f"\nPosting tweet: {tweet_text}")
    try:
        tweet_result = await api.post_tweet(text=tweet_text)
        print(f"Tweet posted successfully!")
        print(f"Tweet ID: {tweet_result.get('id')}")
        print(f"Tweet text: {tweet_result.get('text')}")
    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
