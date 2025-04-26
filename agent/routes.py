from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel

from agent.agent import TwitterAgent, AgentResponse

class AgentQueryRequest(BaseModel):
    query: str
    twitter_user_id: Optional[str] = None
    user_id: Optional[int] = None

# Create router
agent_router = APIRouter()

@agent_router.post("/process", response_model=AgentResponse)
async def process_agent_query(
    query: str = Body(..., description="The query to process"),
    user_id: Optional[int] = Query(None, description="Internal user ID"),
    twitter_user_id: Optional[str] = Query(None, description="Twitter user ID")
):
    """
    Process a query with the Twitter AI agent.
    
    The agent will analyze the query and decide which Twitter operations to perform.
    """
    if not user_id and not twitter_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or twitter_user_id must be provided")
    
    try:
        agent = TwitterAgent()
        return await agent.process_query(query=query, user_id=user_id, twitter_user_id=twitter_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

@agent_router.post("/query", response_model=AgentResponse)
async def process_agent_query_json(request: AgentQueryRequest):
    """
    Process a query with the Twitter AI agent using a JSON request body.
    
    The agent will analyze the query and decide which Twitter operations to perform.
    """
    if not request.user_id and not request.twitter_user_id:
        raise HTTPException(status_code=400, detail="Either user_id or twitter_user_id must be provided")
    
    try:
        agent = TwitterAgent()
        return await agent.process_query(query=request.query, user_id=request.user_id, twitter_user_id=request.twitter_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

@agent_router.get("/")
async def agent_info():
    """
    Return information about the agent API
    """
    return {
        "name": "Twitter Agent API",
        "description": "API for interacting with Twitter using AI agent",
        "endpoints": [
            "/agent/process"
        ],
        "usage": "POST /agent/process with query parameter and either user_id or twitter_user_id"
    }
