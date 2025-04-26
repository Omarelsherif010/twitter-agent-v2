import asyncio
import logging
import os
import sys
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mock_agent import MockAgent

async def test_with_single_user():
    """Test the mock agent with a single user."""
    print("=" * 50)
    print("MOCK AGENT SINGLE USER TEST")
    print("=" * 50)
    print("This test will use mock Twitter data and won't make actual API calls.")
    print("=" * 50)
    
    # Create a mock agent
    agent = MockAgent()
    
    # Mock Twitter user ID
    twitter_user_id = "mock_user_123"
    
    while True:
        query = input("\nEnter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        # Process the query
        response = await agent.process_query(query=query, twitter_user_id=twitter_user_id)
        
        # Display the response
        print("=" * 50)
        print("AGENT RESPONSE:")
        print("=" * 50)
        print(response.response)
        print("=" * 50)
        
        # Display actions taken
        if response.actions_taken:
            print("ACTIONS TAKEN:")
            print("=" * 50)
            for i, action in enumerate(response.actions_taken, 1):
                print(f"--- Action {i}: {action.tool} ---")
                print("Input:")
                for key, value in action.input.items():
                    print(f"  {key}: {value}")
                print("Output:")
                for key, value in action.output.items():
                    print(f"  {key}: {value}")
                print(f"Success: {action.success}")
            print("=" * 50)

async def test_with_multiple_users():
    """Test the mock agent with multiple users."""
    print("=" * 50)
    print("MOCK AGENT MULTIPLE USERS TEST")
    print("=" * 50)
    print("This test will simulate multiple users interacting with the agent.")
    print("=" * 50)
    
    # Create a mock agent
    agent = MockAgent()
    
    # Mock Twitter user IDs
    users = {
        "user1": "mock_user_123",
        "user2": "mock_user_456",
        "user3": "mock_user_789"
    }
    
    current_user = "user1"
    
    while True:
        print(f"\nCurrent user: {current_user} (Twitter ID: {users[current_user]})")
        print("Commands: 'switch user' to change users, 'exit' to quit")
        
        query = input("\nEnter your query: ")
        
        if query.lower() == 'exit':
            break
            
        if query.lower() == 'switch user':
            # Cycle through users
            if current_user == "user1":
                current_user = "user2"
            elif current_user == "user2":
                current_user = "user3"
            else:
                current_user = "user1"
            print(f"Switched to {current_user}")
            continue
            
        # Process the query for the current user
        response = await agent.process_query(query=query, twitter_user_id=users[current_user])
        
        # Display the response
        print("=" * 50)
        print(f"AGENT RESPONSE FOR {current_user}:")
        print("=" * 50)
        print(response.response)
        print("=" * 50)
        
        # Display actions taken
        if response.actions_taken:
            print(f"ACTIONS TAKEN FOR {current_user}:")
            print("=" * 50)
            for i, action in enumerate(response.actions_taken, 1):
                print(f"--- Action {i}: {action.tool} ---")
                print("Input:")
                for key, value in action.input.items():
                    print(f"  {key}: {value}")
                print("Output:")
                for key, value in action.output.items():
                    print(f"  {key}: {value}")
                print(f"Success: {action.success}")
            print("=" * 50)

if __name__ == "__main__":
    # Ask the user which test to run
    print("Choose test mode:")
    print("1. Single mock user")
    print("2. Multiple mock users")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_with_single_user())
    elif choice == "2":
        asyncio.run(test_with_multiple_users())
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")
