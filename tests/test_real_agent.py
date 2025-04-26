import asyncio
import logging
import os
import sys
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent import TwitterAgent

async def test_with_single_user():
    """Test the real agent with a single user."""
    print("=" * 50)
    print("TWITTER AGENT SINGLE USER TEST")
    print("=" * 50)
    print("This test will use the real Twitter API and OpenAI.")
    print("Make sure you have set up the required environment variables.")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        return
    
    # Create a real agent
    agent = TwitterAgent()
    
    # Get the Twitter user ID from tokens.json
    twitter_user_id = None
    try:
        with open('data/tokens.json', 'r') as f:
            tokens = json.load(f)
            if tokens:
                # Use the first token's twitter_user_id
                first_token_key = list(tokens.keys())[0]
                twitter_user_id = tokens[first_token_key].get("twitter_user_id")
                print(f"Using Twitter user ID: {twitter_user_id}")
    except (FileNotFoundError, json.JSONDecodeError, IndexError, KeyError) as e:
        print(f"Error loading tokens: {str(e)}")
        print("Please make sure you have authenticated with Twitter.")
        return
    
    if not twitter_user_id:
        twitter_user_id = input("Enter your Twitter user ID: ")
    
    while True:
        query = input("\nEnter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        # Process the query
        try:
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
        except Exception as e:
            print(f"Error processing query: {str(e)}")

async def test_with_multiple_users():
    """Test the real agent with multiple users."""
    print("=" * 50)
    print("TWITTER AGENT MULTIPLE USERS TEST")
    print("=" * 50)
    print("This test will use the real Twitter API and OpenAI with multiple users.")
    print("Make sure you have set up the required environment variables.")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        return
    
    # Create a real agent
    agent = TwitterAgent()
    
    # Get Twitter user IDs from tokens.json
    users = {}
    try:
        with open('data/tokens.json', 'r') as f:
            tokens = json.load(f)
            if tokens:
                for token_key, token_data in tokens.items():
                    twitter_user_id = token_data.get("twitter_user_id")
                    if twitter_user_id:
                        username = token_data.get("username", f"User {token_key}")
                        users[username] = twitter_user_id
                        print(f"Found user: {username} (Twitter ID: {twitter_user_id})")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading tokens: {str(e)}")
        print("Please make sure you have authenticated with Twitter.")
        return
    
    if not users:
        print("No authenticated users found. Please authenticate with Twitter first.")
        return
    
    # Convert users dict to list for easier cycling
    user_list = list(users.items())
    current_user_index = 0
    
    while True:
        current_username, current_twitter_id = user_list[current_user_index]
        print(f"\nCurrent user: {current_username} (Twitter ID: {current_twitter_id})")
        print("Commands: 'switch user' to change users, 'exit' to quit")
        
        query = input("\nEnter your query: ")
        
        if query.lower() == 'exit':
            break
            
        if query.lower() == 'switch user':
            # Cycle to next user
            current_user_index = (current_user_index + 1) % len(user_list)
            print(f"Switched to {user_list[current_user_index][0]}")
            continue
            
        # Process the query for the current user
        try:
            response = await agent.process_query(query=query, twitter_user_id=current_twitter_id)
            
            # Display the response
            print("=" * 50)
            print(f"AGENT RESPONSE FOR {current_username}:")
            print("=" * 50)
            print(response.response)
            print("=" * 50)
            
            # Display actions taken
            if response.actions_taken:
                print(f"ACTIONS TAKEN FOR {current_username}:")
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
        except Exception as e:
            print(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    # Ask the user which test to run
    print("Choose test mode:")
    print("1. Single user")
    print("2. Multiple users")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_with_single_user())
    elif choice == "2":
        asyncio.run(test_with_multiple_users())
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")
