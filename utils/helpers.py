import datetime
from typing import Dict, Any, Optional

def is_token_expired(expires_at: datetime.datetime) -> bool:
    """
    Check if a token is expired
    
    Args:
        expires_at: The expiration datetime of the token
        
    Returns:
        bool: True if token is expired, False otherwise
    """
    # Add a small buffer (5 minutes) to avoid edge cases
    buffer = datetime.timedelta(minutes=5)
    return datetime.datetime.utcnow() + buffer >= expires_at

def format_twitter_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Twitter API response for consistent output
    
    Args:
        response: The raw response from Twitter API
        
    Returns:
        Dict: Formatted response
    """
    # This is a placeholder for more complex formatting logic
    # that might be needed in the future
    return response

def parse_agent_query(query: str) -> Dict[str, Any]:
    """
    Parse a natural language query from an AI agent
    
    Args:
        query: The natural language query from the agent
        
    Returns:
        Dict: Parsed query with action and parameters
    """
    # This is a placeholder for future implementation
    # In a real implementation, this would use NLP to parse the query
    # and determine the action and parameters
    
    # Example implementation (very basic)
    query = query.lower()
    
    if "tweet" in query and "post" in query:
        # Extract text after "post" or "tweet"
        text = query.split("post", 1)[1] if "post" in query else query.split("tweet", 1)[1]
        return {
            "action": "post_tweet",
            "parameters": {
                "text": text.strip()
            }
        }
    elif "like" in query:
        # This is very simplistic and would need to be improved
        return {
            "action": "like_tweet",
            "parameters": {
                "tweet_id": None  # Would need to extract tweet ID
            }
        }
    elif "follow" in query:
        # This is very simplistic and would need to be improved
        return {
            "action": "follow_user",
            "parameters": {
                "target_user_id": None  # Would need to extract user ID or username
            }
        }
    elif "search" in query:
        # Extract search query
        search_query = query.split("search", 1)[1].strip()
        return {
            "action": "search_tweets",
            "parameters": {
                "query": search_query
            }
        }
    else:
        return {
            "action": "unknown",
            "parameters": {}
        }
