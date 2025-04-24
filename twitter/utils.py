import datetime
from typing import Any, Dict

def serialize_datetime(obj: Any) -> Any:
    """
    Serialize datetime objects to ISO format strings
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return obj

def serialize_tweet_data(tweet_data: Any) -> Dict:
    """
    Convert tweet data to a serializable dictionary
    """
    # Basic tweet info
    result = {
        "id": getattr(tweet_data, "id", None),
        "text": getattr(tweet_data, "text", None),
    }
    
    # Handle created_at
    created_at = getattr(tweet_data, "created_at", None)
    result["created_at"] = serialize_datetime(created_at)
    
    # Additional fields if available
    for field in ["author_id", "conversation_id", "in_reply_to_user_id"]:
        if hasattr(tweet_data, field):
            result[field] = getattr(tweet_data, field)
    
    return result
