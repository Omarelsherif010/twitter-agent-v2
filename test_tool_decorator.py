"""
Test script for the Twitter agent using the @tool decorator approach from smolagents.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from twitter.api import TwitterAPI
from agent.agent import TwitterAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the Twitter agent with smolagents."""
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        return
    
    # User ID 1 is already authenticated with Twitter
    user_id = "1"  # This user ID exists in tokens.json
    twitter_api = TwitterAPI(user_id=user_id)
    await twitter_api.initialize_client()
    
    # Initialize the Twitter agent with debug mode enabled
    try:
        agent = TwitterAgent(model_name="gpt-4o", debug_mode=True)
        logger.info("Successfully initialized TwitterAgent")
    except Exception as e:
        logger.error(f"Error initializing TwitterAgent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # Test query
    test_query = "Show me my recent tweets and then post a tweet saying 'Testing the Twitter agent with smolagents'"
    
    # Process the query using the agent
    try:
        logger.info(f"Processing query: '{test_query}' for user_id: {user_id}")
        response = await agent.process_query(
            query=test_query,
            user_id=user_id
        )
        
        # Print the response
        logger.info(f"Agent response: {response.response}")
        
        # Print actions taken
        if response.actions_taken:
            logger.info(f"Actions taken:")
            for action in response.actions_taken:
                logger.info(f"Tool: {action.tool}")
                logger.info(f"Input: {action.input}")
                logger.info(f"Output: {action.output}")
                logger.info(f"Success: {action.success}")
                logger.info("---")
        else:
            logger.info("No actions were taken by the agent.")
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_agent())
