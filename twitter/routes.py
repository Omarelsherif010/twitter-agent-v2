from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict

from twitter.api import TwitterAPI

# Create router
twitter_router = APIRouter()

async def get_twitter_api(user_id: int = None, twitter_user_id: str = None):
    """
    Dependency to get TwitterAPI instance
    """
    if not user_id and not twitter_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or twitter_user_id must be provided")
    
    api = TwitterAPI(user_id=user_id, twitter_user_id=twitter_user_id)
    await api.initialize_client()
    return api

@twitter_router.get("/user")
async def get_user_info(
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
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
    user_id: Optional[int] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Search for tweets
    """
    api = await get_twitter_api(user_id=user_id, twitter_user_id=twitter_user_id)
    return await api.search_tweets(query=query, limit=limit)

@twitter_router.get("/agent")
async def agent_action(
    query: str,
    user_id: Optional[int] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Endpoint for AI agent to interact with Twitter
    This is a placeholder for future implementation
    """
    # This will be implemented in future iterations
    return {
        "status": "not_implemented",
        "message": "Agent functionality will be implemented in future iterations"
    }
