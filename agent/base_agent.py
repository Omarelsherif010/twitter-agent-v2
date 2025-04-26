"""
Base agent implementation for Twitter AI Agent.

This module provides the core functionality for the Twitter AI Agent.
"""

import os
import logging
from typing import Dict, Any, Optional
from smolagents.models import OpenAIServerModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for AI agents with common initialization and utility methods.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", debug_mode: bool = False):
        """
        Initialize the Base Agent.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment.
            model (str, optional): LLM model to use. Defaults to "gpt-4o".
            debug_mode (bool, optional): Whether to enable debug mode. Defaults to False.
        """
        self.debug_mode = debug_mode
        
        if debug_mode:
            logger.setLevel(logging.DEBUG)
            
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided and not found in environment")
        
        # Initialize LLM
        self.model_name = model
        self.model = OpenAIServerModel(
            model_id=model,
            api_key=api_key
        )
        
        logger.info(f"Base Agent initialized with model: {model}")
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Convert an object to a JSON-serializable format.
        
        Args:
            obj: The object to convert
            
        Returns:
            A JSON-serializable representation of the object
        """
        import json
        import copy
        
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return self._make_serializable(obj.to_dict())
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            try:
                # Try to convert to a basic type
                json.dumps(obj)
                return obj
            except (TypeError, OverflowError):
                # If it can't be converted, return a string representation
                return str(obj)
