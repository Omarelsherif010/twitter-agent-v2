"""
Test script for the Twitter agent using smolagents with CodeAgent approach.
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel
from agent.tools import TwitterTools
from twitter.api import TwitterAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def get_user_id():
    """Get a valid user ID from tokens.json"""
    try:
        tokens_path = os.path.join('data', 'tokens.json')
        if os.path.exists(tokens_path):
            with open(tokens_path, 'r') as f:
                tokens = json.load(f)
                if tokens and len(tokens) > 0:
                    # Return the first user ID
                    return list(tokens.keys())[0]
    except Exception as e:
        logger.error(f"Error getting user ID: {str(e)}")
    
    return None

async def test_agent():
    """Test the Twitter agent with a sample query using CodeAgent approach."""
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        return
    
    # Get a valid user ID
    user_id = await get_user_id()
    if not user_id:
        logger.error("No valid user ID found in tokens.json")
        return
    
    logger.info(f"Using user ID: {user_id}")
    
    # Initialize Twitter API
    twitter_api = TwitterAPI(user_id=user_id)
    await twitter_api.initialize()
    
    # Get Twitter tools
    twitter_tools = TwitterTools(twitter_api)
    tools = twitter_tools.get_tools()
    
    # Initialize LiteLLM model and CodeAgent
    model = LiteLLMModel(model_id="gpt-4o", api_key=api_key)
    agent = CodeAgent(
        tools=tools, 
        model=model, 
        add_base_tools=False,
        system_prompt="You are a helpful Twitter assistant that can perform various Twitter operations. Use the available tools to help the user with their Twitter-related tasks."
    )
    
    # Test queries
    queries = [
        "Search for tweets about artificial intelligence",
        "What are my recent tweets?",
        "Post a tweet saying 'Testing the Twitter agent with smolagents!'"
    ]
    
    for query in queries:
        logger.info(f"Testing query: {query}")
        try:
            # Run the agent
            result = await agent.run_async(query)
            
            # Print the response
            logger.info(f"Agent response: {result.output}")
            
            # Print actions taken (if available in trace)
            if hasattr(result, 'trace') and result.trace:
                for step in result.trace:
                    if hasattr(step, 'tool_calls') and step.tool_calls:
                        for i, tool_call in enumerate(step.tool_calls):
                            logger.info(f"Tool call {i+1}: {tool_call.get('name', '')}")
                            logger.info(f"  Input: {tool_call.get('input', {})}")
                            logger.info(f"  Output: {tool_call.get('output', {})}")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_agent())
