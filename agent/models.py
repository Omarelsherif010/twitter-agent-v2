"""
Data models for the Twitter AI Agent.

This module contains the Pydantic models used by the Twitter AI Agent.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ActionTaken(BaseModel):
    """Model for a single action taken by the agent."""
    tool: str = Field(..., description="The name of the tool that was used")
    input: Dict[str, Any] = Field(default={}, description="The input parameters provided to the tool")
    output: Dict[str, Any] = Field(default={}, description="The output returned by the tool")
    success: bool = Field(default=True, description="Whether the tool execution was successful")

class AgentResponse(BaseModel):
    """Model for agent response."""
    response: str = Field(..., description="The text response from the agent")
    actions_taken: List[ActionTaken] = Field(default=[], description="List of actions taken by the agent")
