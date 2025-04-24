import asyncio
import sys
import json
import datetime
from typing import Dict, Any, List, Optional

from twitter.utils import serialize_datetime

from twitter.api import TwitterAPI
from database.db import get_tokens


async def get_first_active_token() -> Optional[Dict[str, Any]]:
    """
    Get the first active token from the tokens.json file
    """
    tokens = await get_tokens()
    for token_id, token in tokens.items():
        if token.get("is_active", False):
            return token
    return None


async def fetch_user_info(twitter_user_id: str) -> Dict[str, Any]:
    """
    Fetch information about the authenticated user
    """
    api = TwitterAPI(twitter_user_id=twitter_user_id)
    return await api.get_user_info()


async def fetch_timeline(twitter_user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch the user's timeline
    """
    api = TwitterAPI(twitter_user_id=twitter_user_id)
    return await api.get_user_timeline(limit=limit)


async def post_tweet(twitter_user_id: str, text: str) -> Dict[str, Any]:
    """
    Post a new tweet
    """
    api = TwitterAPI(twitter_user_id=twitter_user_id)
    return await api.post_tweet(text=text)


async def main():
    # Get the first active token
    token = await get_first_active_token()
    
    if not token:
        print("No active tokens found. Please authenticate first.")
        return
    
    twitter_user_id = token["twitter_user_id"]
    print(f"Using Twitter account: @{token['twitter_username']}")
    
    # Menu for operations
    while True:
        print("\nTwitter Operations:")
        print("1. Fetch user info")
        print("2. Fetch timeline")
        print("3. Post a tweet")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            # Fetch user info
            print("\nFetching user info...")
            user_info = await fetch_user_info(twitter_user_id)
            # Use our utility function for datetime serialization
            print(json.dumps(user_info, indent=2, default=lambda obj: serialize_datetime(obj) if isinstance(obj, datetime.datetime) else str(obj)))
        
        elif choice == "2":
            # Fetch timeline
            limit = int(input("Enter number of tweets to fetch (default 10): ") or "10")
            print(f"\nFetching {limit} tweets from timeline...")
            timeline = await fetch_timeline(twitter_user_id, limit=limit)
            
            if not timeline:
                print("No tweets found in timeline.")
            else:
                for i, tweet in enumerate(timeline, 1):
                    print(f"\n{i}. Tweet ID: {tweet.get('id')}")
                    print(f"   Text: {tweet.get('text')}")
                    
                    # Handle created_at which might be a datetime object
                    created_at = tweet.get('created_at', 'Unknown')
                    if isinstance(created_at, datetime.datetime):
                        created_at = created_at.isoformat()
                    print(f"   Created at: {created_at}")
        
        elif choice == "3":
            # Post a tweet
            text = input("Enter your tweet text: ")
            if not text:
                print("Tweet text cannot be empty.")
                continue
                
            print("\nPosting tweet...")
            try:
                result = await post_tweet(twitter_user_id, text)
                print(f"Tweet posted successfully!")
                print(f"Tweet ID: {result.get('id')}")
                print(f"Tweet text: {result.get('text')}")
            except Exception as e:
                print(f"Error posting tweet: {str(e)}")
                import traceback
                print(traceback.format_exc())
        
        elif choice == "4":
            # Exit
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())
