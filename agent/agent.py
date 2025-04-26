import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from smolagents import ToolCallingAgent
from pydantic import BaseModel, Field
from openai import OpenAI
from twitter.api import TwitterAPI
from agent.tools import TwitterTools
from database.db import save_tweets

# Set up logging
logging.basicConfig(level=logging.INFO)
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

class TwitterAgent:
    """Twitter AI agent that can interact with Twitter API."""
    
    # Class-level cache for active user sessions
    _user_sessions = {}
    _session_lock = asyncio.Lock()
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.model_name = model_name
        self.openai_client = OpenAI(api_key=self.openai_api_key)
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
    
    async def _call_openai_with_tools(self, query: str, tools: List):
        """
        Call OpenAI API with tools and handle the response.
        """
        # Create function definitions for the tools
        tool_definitions = []
        tool_map = {}
        
        for tool in tools:
            # Handle SimpleTool objects from smolagents
            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                # This is a SimpleTool from smolagents
                func_name = tool.name
                func_desc = tool.description
                
                # Get parameters from the tool's schema if available
                parameters = {}
                required_params = []
                
                if hasattr(tool, 'parameters_schema') and tool.parameters_schema:
                    schema = tool.parameters_schema
                    if 'properties' in schema:
                        parameters = schema['properties']
                    if 'required' in schema:
                        required_params = schema['required']
            else:
                # Fallback for regular functions
                func_name = getattr(tool, '__name__', f"tool_{len(tool_map)}")
                func_desc = getattr(tool, '__doc__', f"Function to perform a Twitter operation")
                
                # Create parameters from function signature
                import inspect
                try:
                    sig = inspect.signature(tool)
                    parameters = {}
                    required_params = []
                    
                    for param_name, param in sig.parameters.items():
                        if param_name == 'self':
                            continue
                            
                        param_type = "string"  # Default type
                        param_desc = f"The {param_name} parameter"
                        
                        parameters[param_name] = {
                            "type": param_type,
                            "description": param_desc
                        }
                        
                        if param.default == inspect.Parameter.empty:
                            required_params.append(param_name)
                except (ValueError, TypeError):
                    # If we can't get the signature, use empty parameters
                    parameters = {}
                    required_params = []
            
            # Create the function definition
            tool_def = {
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": func_desc,
                    "parameters": {
                        "type": "object",
                        "properties": parameters,
                        "required": required_params
                    }
                }
            }
            
            tool_definitions.append(tool_def)
            tool_map[func_name] = tool
        
        # Call OpenAI API
        messages = [
            {"role": "system", "content": "You are a helpful Twitter assistant that can help users interact with Twitter. You can post tweets, search for tweets, view the user's timeline, and get user information."},
            {"role": "user", "content": query}
        ]
        
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto"
        )
        
        # Process the response
        message = response.choices[0].message
        actions_taken = []
        
        # Check if the model wants to call a function
        if message.tool_calls:
            # Process each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Get the function from the tool map
                if function_name in tool_map:
                    tool_func = tool_map[function_name]
                    
                    try:
                        # Call the function with the arguments
                        # Handle SimpleTool objects from smolagents
                        if hasattr(tool_func, '__call__'):
                            # Regular function
                            result = await tool_func(**function_args)
                        elif hasattr(tool_func, 'call'):
                            # SimpleTool from smolagents
                            result = await tool_func.call(**function_args)
                        else:
                            # Unknown tool type
                            raise ValueError(f"Unknown tool type: {type(tool_func)}")
                            
                        # Save tweet data if applicable
                        if session and 'user_id' in session:
                            user_id = session['user_id']
                            # Check if the result contains tweet data
                            if function_name == 'get_timeline_tool' and isinstance(result, dict) and 'tweets' in result:
                                # Save timeline tweets
                                await save_tweets(str(user_id), result['tweets'], tweet_type="timeline")
                                logger.info(f"Saved {len(result['tweets'])} timeline tweets for user {user_id}")
                            elif function_name == 'search_tweets_tool' and isinstance(result, dict) and 'tweets' in result:
                                # Save search tweets
                                query = function_args.get('query', 'unknown')
                                await save_tweets(str(user_id), result['tweets'], tweet_type=f"search_{query}")
                                logger.info(f"Saved {len(result['tweets'])} search tweets for user {user_id}")
                            elif function_name == 'post_tweet_tool' and isinstance(result, dict) and 'success' in result and result['success']:
                                # Save posted tweet
                                tweet_data = {
                                    'id': result.get('tweet_id', ''),
                                    'text': result.get('text', function_args.get('text', ''))
                                }
                                await save_tweets(str(user_id), [tweet_data], tweet_type="posted")
                                logger.info(f"Saved posted tweet for user {user_id}")
                            
                        success = True
                    except Exception as e:
                        logger.error(f"Error calling tool {function_name}: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        result = {"error": str(e)}
                        success = False
                    
                    # Add the action to the list
                    actions_taken.append(ActionTaken(
                        tool=function_name,
                        input=function_args,
                        output=result,
                        success=success
                    ))
        
        # Get the final response
        if actions_taken:
            # If we called tools, send the results back to the model for a final response
            messages.append(message)  # Add the assistant's message with tool calls
            
            # Add the tool results to the messages
            for action in actions_taken:
                messages.append({
                    "role": "tool",
                    "tool_call_id": message.tool_calls[actions_taken.index(action)].id,
                    "name": action.tool,
                    "content": json.dumps(action.output)
                })
            
            # Get the final response from the model
            final_response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            
            response_text = final_response.choices[0].message.content
        else:
            # If no tools were called, use the original response
            response_text = message.content
        
        return response_text, actions_taken
    
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
            
            # Call OpenAI with the tools
            response_text, actions_taken = await self._call_openai_with_tools(
                query=query, 
                tools=twitter_tools.get_tools()
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
