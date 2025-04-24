import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class User(BaseModel):
    """
    User model to store basic user information
    """
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for JSON storage
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create model from dictionary
        """
        # Convert string dates to datetime objects
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)

class TwitterToken(BaseModel):
    """
    Model to store OAuth 2.0 tokens for Twitter API
    """
    id: Optional[str] = None
    user_id: str
    twitter_user_id: str
    twitter_username: str
    
    # OAuth 2.0 tokens
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: datetime.datetime
    
    # Token metadata
    scopes: str = ""  # Comma-separated list of granted scopes
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for JSON storage
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "twitter_user_id": self.twitter_user_id,
            "twitter_username": self.twitter_username,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
            "scopes": self.scopes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TwitterToken':
        """
        Create model from dictionary
        """
        # Convert string dates to datetime objects
        if isinstance(data.get("expires_at"), str):
            data["expires_at"] = datetime.datetime.fromisoformat(data["expires_at"])
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.datetime.fromisoformat(data["updated_at"])
            
        return cls(**data)
