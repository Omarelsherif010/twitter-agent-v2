from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict

from twitter.api import TwitterAPI
from database.db import get_saved_tweets

# Create router
twitter_router = APIRouter()

async def get_twitter_api(user_id: Optional[str] = None, twitter_user_id: Optional[str] = None):
    """
    Dependency to get TwitterAPI instance
    """
    if not user_id and not twitter_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or twitter_user_id must be provided")
    
    # Convert user_id to int if it's a string
    user_id_int = None
    if user_id:
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format")
    
    api = TwitterAPI(user_id=user_id_int, twitter_user_id=twitter_user_id)
    await api.initialize_client()
    return api

@twitter_router.get("/user")
async def get_user_info(
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Get information about the authenticated user
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.get_user_info()

@twitter_router.post("/tweet")
async def post_tweet(
    text: str,
    reply_to_id: Optional[str] = None,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Post a new tweet
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.post_tweet(text=text, reply_to_id=reply_to_id)

@twitter_router.get("/tweet/{tweet_id}")
async def get_tweet(
    tweet_id: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Get a specific tweet by ID
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.get_tweet(tweet_id=tweet_id)

@twitter_router.post("/like/{tweet_id}")
async def like_tweet(
    tweet_id: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Like a tweet
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.like_tweet(tweet_id=tweet_id)

@twitter_router.post("/unlike/{tweet_id}")
async def unlike_tweet(
    tweet_id: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Unlike a tweet
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.unlike_tweet(tweet_id=tweet_id)

@twitter_router.post("/follow/{target_user_id}")
async def follow_user(
    target_user_id: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Follow a user
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.follow_user(target_user_id=target_user_id)

@twitter_router.post("/unfollow/{target_user_id}")
async def unfollow_user(
    target_user_id: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Unfollow a user
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.unfollow_user(target_user_id=target_user_id)

@twitter_router.get("/timeline")
async def get_user_timeline(
    limit: int = 10,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Get the user's timeline
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.get_user_timeline(limit=limit)

@twitter_router.get("/search")
async def search_tweets(
    query: str,
    limit: int = 10,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Search for tweets
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.search_tweets(query=query, limit=limit)

@twitter_router.get("/saved-tweets")
async def get_user_saved_tweets(
    user_id: str = Query(..., description="Internal user ID"),
    tweet_type: Optional[str] = Query(None, description="Type of tweets to retrieve (timeline, search, posted)"),
    limit: int = Query(10, description="Maximum number of tweet files to return")
):
    """
    Retrieve saved tweets for a user
    """
    # Get saved tweets from JSON files
    saved_tweets = await get_saved_tweets(user_id=user_id, tweet_type=tweet_type, limit=limit)
    
    return {
        "user_id": user_id,
        "tweet_type": tweet_type or "all",
        "count": len(saved_tweets),
        "saved_tweets": saved_tweets
    }

@twitter_router.get("/agent")
async def agent_action(
    query: str,
    user_id: Optional[str] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Endpoint for AI agent to interact with Twitter
    """
    from agent.agent import TwitterAgent
    
    if not user_id and not twitter_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or twitter_user_id must be provided")
    
    try:
        # Initialize the Twitter agent
        agent = TwitterAgent()
        
        # Process the query
        response = await agent.process_query(query=query, user_id=user_id, twitter_user_id=twitter_user_id)
        
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Agent error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")
