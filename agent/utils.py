"""
Utility functions for the Twitter Agent.

This module provides helper functions for the Twitter Agent implementation.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_timestamped_filename(prefix: str, extension: str) -> str:
    """
    Generate a filename with a timestamp.
    
    Args:
        prefix: Prefix for the filename
        extension: File extension (without the dot)
        
    Returns:
        A filename with format: prefix_YYYYMMDD_HHMMSS.extension
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def make_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format.
    
    Args:
        obj: The object to convert
        
    Returns:
        A JSON-serializable representation of the object
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return make_serializable(obj.to_dict())
    elif hasattr(obj, '__dict__'):
        return make_serializable(obj.__dict__)
    else:
        try:
            # Try to convert to a basic type
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            # If it can't be converted, return a string representation
            return str(obj)

def save_json(data: Any, filepath: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert data to JSON-serializable format
        serializable_data = make_serializable(data)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {str(e)}")
        return False
