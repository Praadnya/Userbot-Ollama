from pydantic import BaseModel, Field
from typing import Optional, Dict

class UserRequest(BaseModel):
    """
    Represents a complete user request with query and optional user data.
    """
    user_query: str = Field(..., min_length=1, max_length=1000)
    user_data: str