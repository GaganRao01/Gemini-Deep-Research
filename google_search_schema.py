"""
Schema definitions for the Google Custom Search Tool
"""

from typing import Optional
from pydantic import BaseModel, Field

class GoogleCustomSearchToolSchema(BaseModel):
    """Schema for the Google Custom Search Tool input parameters"""
    query: str = Field(description="The search query string")
    num_results: int = Field(default=3, description="Number of results to return (1-10)")
    site_search: Optional[str] = None  # Make site_search truly optional at the schema level 