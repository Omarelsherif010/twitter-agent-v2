import asyncio
import os
import json
from dotenv import load_dotenv

from agent.agent import TwitterAgent
from database.db import init_db

async def main():
    """
    Test the Twitter AI agent functionality
    """
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please add it to your .env file")
        return
        
    # Initialize database
    await init_db()
    
    # Get Twitter user ID from input
    twitter_user_id = input("Enter Twitter user ID: ")
    
    # Create the agent
    agent = TwitterAgent()
    
    # Process queries in a loop
    while True:
        # Get user query
        query = input("\nEnter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        print("\nProcessing your query...")
        
        try:
            # Process the query
            response = await agent.process_query(query=query, twitter_user_id=twitter_user_id)
            
            # Print the response
            print("\nAgent Response:")
            print(response.response)
            
            # Print actions taken
            if response.actions_taken:
                print("\nActions Taken:")
                for i, action in enumerate(response.actions_taken, 1):
                    print(f"\n--- Action {i} ---")
                    print(f"Tool: {action.tool}")
                    print(f"Input: {json.dumps(action.input, indent=2)}")
                    print(f"Output: {json.dumps(action.output, indent=2)}")
                    print(f"Success: {action.success}")
            else:
                print("\nNo actions were taken.")
        
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
