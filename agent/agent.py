"""Twitter AI Agent implementation using smolagents.

This module provides an AI agent that can understand natural language queries
and perform appropriate Twitter operations based on user intent.
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from smolagents import CodeAgent

from twitter.api import TwitterAPI
from agent.tools import TwitterTools
from agent.base_agent import BaseAgent
from agent.prompts import AgentPrompts
from agent.models import ActionTaken, AgentResponse
from database.db import save_tweets

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterAgent(BaseAgent):
    """Twitter AI agent that can interact with Twitter API using smolagents."""
    
    # Dictionary to store user sessions
    _user_sessions = {}
    _session_lock = asyncio.Lock()
    
    def __init__(self, model_name: str = "gpt-4o", debug_mode: bool = False):
        # Initialize the base agent
        super().__init__(model=model_name, debug_mode=debug_mode)
        logger.info(f"Initialized TwitterAgent with model: {model_name}")
    
    async def _get_user_session(self, user_id: Optional[Any] = None, twitter_user_id: Optional[str] = None) -> Dict:
        """
        Get or create a user session for the given user.
        
        Args:
            user_id: Optional internal user ID (can be int or str).
            twitter_user_id: Optional Twitter user ID (preferred for authentication).
            
        Returns:
            User session dictionary containing the Twitter API and tools.
        """
        # Convert user_id to string if it's not None
        user_id_str = str(user_id) if user_id is not None else None
        
        # Create a unique session key
        session_key = f"user_{user_id_str}" if user_id_str else f"twitter_{twitter_user_id}"
        
        async with self._session_lock:
            # Check if session exists and is still valid
            if session_key in self._user_sessions:
                # Check if session is expired (for future implementation)
                return self._user_sessions[session_key]
            
            # Create a new session
            logger.info(f"Creating new session for {session_key}")
            
            # Initialize Twitter API
            twitter_api = TwitterAPI(user_id=user_id, twitter_user_id=twitter_user_id)
            await twitter_api.initialize_client()
            
            # Create Twitter tools
            twitter_tools = TwitterTools(twitter_api)
            
            # Store session
            session = {
                "twitter_api": twitter_api,
                "twitter_tools": twitter_tools,
                "created_at": asyncio.get_event_loop().time(),
                "last_used": asyncio.get_event_loop().time()
            }
            
            self._user_sessions[session_key] = session
            
            # Implement session cleanup (remove old sessions after a certain time)
            asyncio.create_task(self._cleanup_old_sessions())
            
            return session
    
    async def _cleanup_old_sessions(self, max_age: float = 3600):
        """
        Cleanup old sessions that haven't been used for a while.
        
        Args:
            max_age: Maximum age of sessions in seconds before cleanup (default: 1 hour).
        """
        current_time = asyncio.get_event_loop().time()
        
        async with self._session_lock:
            # Find sessions to remove
            sessions_to_remove = []
            for key, session in self._user_sessions.items():
                if current_time - session["last_used"] > max_age:
                    sessions_to_remove.append(key)
            
            # Remove old sessions
            for key in sessions_to_remove:
                logger.info(f"Cleaning up old session: {key}")
                del self._user_sessions[key]
    

    
    async def _run_agent_with_tools(self, query: str, tools: List, session: Optional[Dict] = None):
        """
        Run the agent with the provided tools and handle the response.
        """
        # Create a smolagents CodeAgent with the provided tools
        try:
            agent = CodeAgent(
                model=self.model,
                tools=tools,
                add_base_tools=False,  # Don't add default tools
                system_prompt=AgentPrompts.get_twitter_assistant_prompt(),
                additional_authorized_imports=[]  # No additional imports needed for Twitter operations
            )
        except Exception as e:
            logger.error(f"Error creating CodeAgent: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"I encountered an error while initializing the agent: {str(e)}. Please try again.", []
        
        # Run the agent with the query
        logger.info(f"Running agent with query: {query}")
        try:
            # Use run_async for async execution
            result = await agent.run_async(query)
            
            # Extract the actions taken from the agent's trace
            actions_taken = []
            
            # Process the trace to extract tool calls
            if hasattr(result, 'trace') and result.trace:
                for step in result.trace:
                    # Check for code execution steps
                    if hasattr(step, 'code') and step.code:
                        logger.info(f"Agent executed code: {step.code}")
                    
                    # Check for tool calls
                    if hasattr(step, 'tool_calls') and step.tool_calls:
                        for tool_call in step.tool_calls:
                            tool_name = tool_call.get('name', '')
                            tool_input = tool_call.get('input', {})
                            tool_output = tool_call.get('output', {})
                            success = True if 'error' not in tool_output else False
                            
                            # Save tweet data if applicable
                            if session and 'twitter_api' in session:
                                user_id = session['twitter_api'].user_id
                                if user_id:
                                    # Check if the result contains tweet data
                                    if tool_name == 'get_timeline_tool' and isinstance(tool_output, dict) and 'tweets' in tool_output:
                                        # Save timeline tweets
                                        await save_tweets(str(user_id), tool_output['tweets'], tweet_type="timeline")
                                        logger.info(f"Saved {len(tool_output['tweets'])} timeline tweets for user {user_id}")
                                    elif tool_name == 'search_tweets_tool' and isinstance(tool_output, dict) and 'tweets' in tool_output:
                                        # Save search tweets
                                        search_query = tool_input.get('query', 'unknown')
                                        await save_tweets(str(user_id), tool_output['tweets'], tweet_type=f"search_{search_query}")
                                        logger.info(f"Saved {len(tool_output['tweets'])} search tweets for user {user_id}")
                                    elif tool_name == 'post_tweet_tool' and isinstance(tool_output, dict) and 'success' in tool_output and tool_output['success']:
                                        # Save posted tweet
                                        tweet_data = {
                                            'id': tool_output.get('tweet_id', ''),
                                            'text': tool_output.get('text', tool_input.get('text', ''))
                                        }
                                        await save_tweets(str(user_id), [tweet_data], tweet_type="posted")
                                        logger.info(f"Saved posted tweet for user {user_id}")
                            
                            actions_taken.append(ActionTaken(
                                tool=tool_name,
                                input=tool_input,
                                output=tool_output,
                                success=success
                            ))
            
            # Post-process the result
            result_output = result.output
            # Make the result serializable if needed
            actions_taken = self._make_serializable(actions_taken)
            
            return result_output, actions_taken
            
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"I encountered an error while processing your request: {str(e)}. Please try again.", []
    
    async def process_query(self, 
                           query: str, 
                           user_id: Optional[Any] = None, 
                           twitter_user_id: Optional[str] = None) -> AgentResponse:
        """
        Process a user query and perform Twitter operations as needed.
        
        Args:
            query: The user's query or instruction.
            user_id: Optional internal user ID.
            twitter_user_id: Optional Twitter user ID (preferred for authentication).
            
        Returns:
            Agent response with actions taken.
        """
        logger.info(f"Processing query: '{query}' for user_id={user_id}, twitter_user_id={twitter_user_id}")
        
        try:
            # Get or create user session
            session = await self._get_user_session(user_id=user_id, twitter_user_id=twitter_user_id)
            
            # Update last used timestamp
            session["last_used"] = asyncio.get_event_loop().time()
            
            # Get the Twitter tools from the session
            twitter_tools = session["twitter_tools"]
            
            # Run the agent with the tools
            response_text, actions_taken = await self._run_agent_with_tools(
                query=query, 
                tools=twitter_tools.create_tools(),
                session=session
            )
            
            logger.info(f"Agent completed with {len(actions_taken)} actions taken")
            
            # Return the agent's response and actions taken
            return AgentResponse(
                response=response_text,
                actions_taken=actions_taken
            )
            
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # Return a graceful error response
            return AgentResponse(
                response=f"I encountered an error while processing your request: {str(e)}. Please try again or contact support if the issue persists.",
                actions_taken=[]
            )
