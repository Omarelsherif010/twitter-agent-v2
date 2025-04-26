import logging
import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from tests.mock_api import MockTwitterAPI
from tests.mock_tools import MockTwitterTools

logger = logging.getLogger(__name__)

class ActionTaken(BaseModel):
    """Model for a single action taken by the agent."""
    tool: str = Field(..., description="The name of the tool that was used")
    input: Dict[str, Any] = Field(default={}, description="The input parameters provided to the tool")
    output: Dict[str, Any] = Field(default={}, description="The output returned by the tool")
    success: bool = Field(default=True, description="Whether the tool execution was successful")

class AgentResponse(BaseModel):
    """Model for agent response."""
    response: str = Field(..., description="The text response from the agent")
    actions_taken: List[ActionTaken] = Field(default=[], description="List of actions taken by the agent")

class MockAgent:
    """Mock Twitter AI agent for testing."""
    
    def __init__(self):
        """Initialize the mock agent."""
        self.sessions = {}
        logger.info("Initialized MockAgent")
    
    async def process_query(self, query: str, user_id: Optional[int] = None, twitter_user_id: Optional[str] = None):
        """
        Process a mock query and simulate Twitter operations.
        
        Args:
            query: The user's query or instruction.
            user_id: Optional internal user ID.
            twitter_user_id: Optional Twitter user ID.
            
        Returns:
            A mock response with simulated actions.
        """
        logger.info(f"Processing mock query: '{query}' for user_id={user_id}, twitter_user_id={twitter_user_id}")
        
        # Create a session key
        session_key = f"user_{user_id}" if user_id else f"twitter_{twitter_user_id}"
        
        # Get or create session
        if session_key not in self.sessions:
            # Create a new session with mock Twitter API
            mock_api = MockTwitterAPI(user_id=user_id, twitter_user_id=twitter_user_id)
            await mock_api.initialize_client()
            self.sessions[session_key] = {
                "api": mock_api,
                "tools": MockTwitterTools(mock_api)
            }
        
        session = self.sessions[session_key]
        tools = session["tools"]
        
        # Analyze the query to determine which action to take
        actions_taken = []
        response_text = ""
        
        # Simple keyword-based action selection for testing
        if "post" in query.lower() and "tweet" in query.lower():
            # Extract the tweet text - simple implementation for testing
            tweet_text = query.split("post tweet", 1)[1].strip() if "post tweet" in query.lower() else "This is a mock tweet!"
            
            # Call the post_tweet tool
            result = await tools.post_tweet(text=tweet_text)
            actions_taken.append({
                "tool": "post_tweet_tool",
                "input": {"text": tweet_text},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I've posted your tweet: '{tweet_text}'"
            
        elif "timeline" in query.lower():
            # Call the get_timeline tool
            result = await tools.get_user_timeline(limit=5)
            actions_taken.append({
                "tool": "get_timeline_tool",
                "input": {"limit": 5},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = "Here's your recent timeline."
            
        elif "search" in query.lower() and "tweet" in query.lower():
            # Extract the search query - simple implementation for testing
            search_terms = query.split("search", 1)[1].strip()
            if "for" in search_terms:
                search_terms = search_terms.split("for", 1)[1].strip()
            
            # Call the search_tweets tool
            result = await tools.search_tweets(query=search_terms, limit=5)
            actions_taken.append({
                "tool": "search_tweets_tool",
                "input": {"query": search_terms, "limit": 5},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I searched for tweets matching '{search_terms}'."
            
        elif "profile" in query.lower() or "user info" in query.lower():
            # Call the get_user_info tool
            result = await tools.get_user_info()
            actions_taken.append({
                "tool": "get_user_info_tool",
                "input": {},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = "Here's your profile information."
            
        elif "like" in query.lower() and not "unlike" in query.lower():
            # Mock tweet ID for testing
            tweet_id = "tweet_123456"
            
            # Call the like_tweet tool
            result = await tools.like_tweet(tweet_id=tweet_id)
            actions_taken.append({
                "tool": "like_tweet_tool",
                "input": {"tweet_id": tweet_id},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I've liked the tweet with ID {tweet_id}."
            
        elif "unlike" in query.lower():
            # Mock tweet ID for testing
            tweet_id = "tweet_123456"
            
            # Call the unlike_tweet tool
            result = await tools.unlike_tweet(tweet_id=tweet_id)
            actions_taken.append({
                "tool": "unlike_tweet_tool",
                "input": {"tweet_id": tweet_id},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I've unliked the tweet with ID {tweet_id}."
            
        elif "follow" in query.lower() and not "unfollow" in query.lower():
            # Mock user ID for testing
            target_user_id = "user_789012"
            
            # Call the follow_user tool
            result = await tools.follow_user(target_user_id=target_user_id)
            actions_taken.append({
                "tool": "follow_user_tool",
                "input": {"target_user_id": target_user_id},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I've followed the user with ID {target_user_id}."
            
        elif "unfollow" in query.lower():
            # Mock user ID for testing
            target_user_id = "user_789012"
            
            # Call the unfollow_user tool
            result = await tools.unfollow_user(target_user_id=target_user_id)
            actions_taken.append({
                "tool": "unfollow_user_tool",
                "input": {"target_user_id": target_user_id},
                "output": result,
                "success": result.get("success", True)
            })
            
            response_text = f"I've unfollowed the user with ID {target_user_id}."
            
        else:
            # Default response for testing
            response_text = "I'm not sure what you want to do. You can ask me to post a tweet, view your timeline, search for tweets, view your profile, like/unlike tweets, or follow/unfollow users."
        
        # Convert the actions to ActionTaken objects
        action_objects = []
        for action in actions_taken:
            action_objects.append(ActionTaken(
                tool=action["tool"],
                input=action["input"],
                output=action["output"],
                success=action["success"]
            ))
        
        return AgentResponse(
            response=response_text,
            actions_taken=action_objects
        )
