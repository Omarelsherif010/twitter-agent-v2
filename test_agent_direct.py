import asyncio
import os
import logging
from agent.agent import TwitterAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent():
    """
    Test the Twitter agent directly without using the FastAPI endpoint.
    """
    # Twitter user ID to use for testing
    twitter_user_id = "1171863380891770882"  # Replace with your Twitter user ID
    
    # Create the agent
    agent = TwitterAgent()
    
    # Process a query
    query = "Search for 5 tweets about AI and then post a new tweet saying 'I just searched for AI tweets using my Twitter Agent. Found some interesting discussions on artificial intelligence!'"
    
    try:
        # Process the query
        response = await agent.process_query(query=query, twitter_user_id=twitter_user_id)
        
        # Print the response
        print("\nAgent Response:")
        print(response.response)
        
        # Print the actions taken
        print("\nActions Taken:")
        for i, action in enumerate(response.actions_taken):
            print(f"\nAction {i+1}:")
            print(f"Tool: {action.tool}")
            print(f"Input: {action.input}")
            print(f"Output: {action.output}")
            print(f"Success: {action.success}")
            
    except Exception as e:
        logger.error(f"Error testing agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_agent())
