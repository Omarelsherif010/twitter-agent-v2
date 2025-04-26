import json
import os
import logging
import aiofiles
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Define file paths
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TOKENS_FILE = os.path.join(DATA_DIR, 'tokens.json')

# File locks to prevent race conditions
users_lock = asyncio.Lock()
tokens_lock = asyncio.Lock()

async def init_db():
    """
    Initialize the JSON storage files if they don't exist
    """
    # Create users.json if it doesn't exist
    if not os.path.exists(USERS_FILE):
        async with aiofiles.open(USERS_FILE, 'w') as f:
            await f.write(json.dumps({}))
    
    # Create tokens.json if it doesn't exist
    if not os.path.exists(TOKENS_FILE):
        async with aiofiles.open(TOKENS_FILE, 'w') as f:
            await f.write(json.dumps({}))

async def read_json_file(file_path: str) -> Dict:
    """
    Read and parse a JSON file
    """
    try:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content) if content else {}
    except FileNotFoundError:
        # If file doesn't exist, return empty dict
        return {}
    except json.JSONDecodeError:
        # If JSON is invalid, return empty dict
        return {}

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def write_json_file(file_path: str, data: Dict) -> None:
    """
    Write data to a JSON file
    """
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(data, indent=2, cls=DateTimeEncoder))

# User operations
async def get_users() -> Dict[str, Any]:
    """
    Get all users
    """
    async with users_lock:
        return await read_json_file(USERS_FILE)

async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID
    """
    users = await get_users()
    return users.get(user_id)

async def create_user(user_data: Dict[str, Any]) -> str:
    """
    Create a new user
    """
    async with users_lock:
        users = await read_json_file(USERS_FILE)
        
        # Generate a new user ID
        user_id = str(len(users) + 1)
        
        # Add user ID to user data
        user_data['id'] = user_id
        
        # Add user to users dict
        users[user_id] = user_data
        
        # Write updated users to file
        await write_json_file(USERS_FILE, users)
        
        return user_id

async def update_user(user_id: str, user_data: Dict[str, Any]) -> bool:
    """
    Update an existing user
    """
    async with users_lock:
        users = await read_json_file(USERS_FILE)
        
        if user_id not in users:
            return False
        
        # Update user data
        users[user_id].update(user_data)
        
        # Write updated users to file
        await write_json_file(USERS_FILE, users)
        
        return True

# Token operations
async def get_tokens() -> Dict[str, Any]:
    """
    Get all tokens
    """
    async with tokens_lock:
        return await read_json_file(TOKENS_FILE)

async def get_token(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a token by ID
    """
    tokens = await get_tokens()
    return tokens.get(token_id)

async def get_token_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a token by user ID
    """
    tokens = await get_tokens()
    
    for token_id, token_data in tokens.items():
        # Convert stored user_id to string for comparison if it's not already a string
        stored_user_id = str(token_data.get('user_id', '')) if token_data.get('user_id') is not None else ''
        
        # Check if the user_id matches and the token is active
        if stored_user_id == str(user_id) and token_data.get('is_active', False):
            return token_data
    
    return None

async def get_token_by_twitter_user_id(twitter_user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a token by Twitter user ID
    """
    tokens = await get_tokens()
    
    for token_id, token_data in tokens.items():
        # Convert stored twitter_user_id to string for comparison if it's not already a string
        stored_twitter_user_id = str(token_data.get('twitter_user_id', '')) if token_data.get('twitter_user_id') is not None else ''
        
        # Check if the twitter_user_id matches and the token is active
        if stored_twitter_user_id == str(twitter_user_id) and token_data.get('is_active', False):
            return token_data
    
    return None


# Tweet storage functions
async def save_tweets(user_id: str, tweets: List[Dict], tweet_type: str = "timeline") -> bool:
    """
    Save tweets to a JSON file for a specific user
    
    Args:
        user_id: The user ID associated with the tweets
        tweets: List of tweet data to save
        tweet_type: Type of tweets (timeline, search, posted)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create tweets directory if it doesn't exist
        tweets_dir = os.path.join(DATA_DIR, "tweets")
        os.makedirs(tweets_dir, exist_ok=True)
        
        # Create user-specific directory
        user_tweets_dir = os.path.join(tweets_dir, str(user_id))
        os.makedirs(user_tweets_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tweet_type}_{timestamp}.json"
        file_path = os.path.join(user_tweets_dir, filename)
        
        # Save tweets to file
        async with aiofiles.open(file_path, "w") as f:
            await f.write(json.dumps({
                "tweet_type": tweet_type,
                "timestamp": timestamp,
                "tweets": tweets
            }, indent=2))
            
        return True
    except Exception as e:
        logger.error(f"Error saving tweets: {str(e)}")
        return False


async def get_saved_tweets(user_id: str, tweet_type: str = None, limit: int = 10) -> List[Dict]:
    """
    Get saved tweets for a specific user
    
    Args:
        user_id: The user ID to get tweets for
        tweet_type: Optional type filter (timeline, search, posted)
        limit: Maximum number of tweet files to return
        
    Returns:
        List of tweet data dictionaries
    """
    try:
        user_tweets_dir = os.path.join(DATA_DIR, "tweets", str(user_id))
        
        # Check if directory exists
        if not os.path.exists(user_tweets_dir):
            return []
        
        # Get list of tweet files
        files = [f for f in os.listdir(user_tweets_dir) if f.endswith(".json")]
        
        # Filter by tweet type if specified
        if tweet_type:
            files = [f for f in files if f.startswith(f"{tweet_type}_")]
        
        # Sort by timestamp (newest first)
        files.sort(reverse=True)
        
        # Limit the number of files
        files = files[:limit]
        
        # Load tweet data from files
        result = []
        for filename in files:
            file_path = os.path.join(user_tweets_dir, filename)
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                data = json.loads(content)
                result.append(data)
        
        return result
    except Exception as e:
        logger.error(f"Error getting saved tweets: {str(e)}")
        return []

async def create_token(token_data: Dict[str, Any]) -> str:
    """
    Create a new token
    """
    async with tokens_lock:
        tokens = await read_json_file(TOKENS_FILE)
        
        # Generate a new token ID
        token_id = str(len(tokens) + 1)
        
        # Add token ID to token data
        token_data['id'] = token_id
        
        # Add token to tokens dict
        tokens[token_id] = token_data
        
        # Write updated tokens to file
        await write_json_file(TOKENS_FILE, tokens)
        
        return token_id

async def update_token(token_id: str, token_data: Dict[str, Any]) -> bool:
    """
    Update an existing token
    """
    async with tokens_lock:
        tokens = await read_json_file(TOKENS_FILE)
        
        if token_id not in tokens:
            return False
        
        # Update token data
        tokens[token_id].update(token_data)
        
        # Write updated tokens to file
        await write_json_file(TOKENS_FILE, tokens)
        
        return True

async def update_token_by_user_id(user_id: str, token_data: Dict[str, Any]) -> bool:
    """
    Update a token by user ID
    """
    async with tokens_lock:
        tokens = await read_json_file(TOKENS_FILE)
        
        for token_id, current_token_data in tokens.items():
            if current_token_data.get('user_id') == user_id:
                # Update token data
                tokens[token_id].update(token_data)
                
                # Write updated tokens to file
                await write_json_file(TOKENS_FILE, tokens)
                
                return True
        
        return False
