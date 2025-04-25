import os
import json
import logging
from typing import Dict, List, Optional, Any
from smolagents import ToolCallingAgent
from smolagents.models import OpenAIServerModel
from pydantic import BaseModel, Field

from agent.tools import TwitterTools
from twitter.api import TwitterAPI

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
    """Twitter AI agent that can interact with Twitter API using smolagents."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        # Store model name for later use
        self.model_name = model_name
        logger.info(f"Initialized TwitterAgent with model: {model_name}")
    
    async def process_query(self, 
                           query: str, 
                           user_id: Optional[int] = None, 
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
            # Initialize Twitter API - prefer twitter_user_id if available due to token storage structure
            twitter_api = TwitterAPI(user_id=user_id, twitter_user_id=twitter_user_id)
            await twitter_api.initialize_client()
            
            # Create Twitter tools
            twitter_tools = TwitterTools(twitter_api)
            
            # Create agent with Twitter tools
            from openai import OpenAI
            
            # Initialize OpenAI client
            openai_client = OpenAI(api_key=self.openai_api_key)
            
            # Get the tools
            tools = twitter_tools.get_tools()
            
            # Prepare the messages
            messages = [
                {"role": "system", "content": "You are a helpful Twitter assistant that can help users interact with Twitter. You can post tweets, search for tweets, view the user's timeline, and get user information."},
                {"role": "user", "content": query}
            ]
            
            # Call the OpenAI API directly
            response = openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": tool.__name__,
                        "description": tool.__doc__,
                        "parameters": tool.__annotations__
                    }
                } for tool in tools],
                tool_choice="auto"
            )
            
            # Process the response
            logger.info("Processing OpenAI response")
            
            response_text = response.choices[0].message.content or ""
            actions_taken = []
            
            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    
                    # Find the matching tool
                    tool_func = next((t for t in tools if t.__name__ == tool_name), None)
                    tool_output = ""
                    success = True
                    
                    if tool_func:
                        try:
                            # Execute the tool
                            tool_output = await tool_func(**tool_input)
                        except Exception as e:
                            tool_output = f"Error executing tool: {str(e)}"
                            success = False
                    else:
                        tool_output = f"Tool {tool_name} not found"
                        success = False
                    
                    actions_taken.append(ActionTaken(
                        tool=tool_name,
                        input=tool_input,
                        output=tool_output,
                        success=success
                    ))
            
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
