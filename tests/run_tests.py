import asyncio
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def main():
    """Main entry point for running tests."""
    print("=" * 50)
    print("TWITTER AGENT V2 TESTING")
    print("=" * 50)
    print("Choose a test to run:")
    print("1. Mock Agent Test (No API calls)")
    print("2. Real Agent Test (Requires Twitter and OpenAI API)")
    print("=" * 50)
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        # Import and run mock agent test
        from tests.test_mock_agent import test_with_single_user, test_with_multiple_users
        
        print("\nChoose mock test mode:")
        print("1. Single mock user")
        print("2. Multiple mock users")
        
        mode = input("Enter your choice (1 or 2): ")
        
        if mode == "1":
            await test_with_single_user()
        elif mode == "2":
            await test_with_multiple_users()
        else:
            print("Invalid choice.")
            
    elif choice == "2":
        # Import and run real agent test
        from tests.test_real_agent import test_with_single_user, test_with_multiple_users
        
        print("\nChoose real test mode:")
        print("1. Single user")
        print("2. Multiple users")
        
        mode = input("Enter your choice (1 or 2): ")
        
        if mode == "1":
            await test_with_single_user()
        elif mode == "2":
            await test_with_multiple_users()
        else:
            print("Invalid choice.")
            
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())
