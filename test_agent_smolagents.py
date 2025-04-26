"""
Simple test script for the Twitter agent using smolagents with CodeAgent.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from agent.agent import TwitterAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the Twitter agent with a sample query."""
    # Create a Twitter agent
    agent = TwitterAgent()
    
    # Test with a simple query
    query = "Search for tweets about artificial intelligence"
    
    try:
        # Process the query
        response = await agent.process_query(query=query)
        
        # Print the response
        logger.info(f"Agent response: {response.response}")
        
        # Print actions taken
        logger.info(f"Actions taken: {len(response.actions_taken)}")
        for i, action in enumerate(response.actions_taken):
            logger.info(f"Action {i+1}: {action.tool}")
            logger.info(f"  Input: {action.input}")
            logger.info(f"  Output: {action.output}")
            logger.info(f"  Success: {action.success}")
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_agent())
