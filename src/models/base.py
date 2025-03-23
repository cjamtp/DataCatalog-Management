"""Base model class for all data catalog entities."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CatalogEntity(BaseModel):
    """Base class for all catalog entities."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CatalogEntity":
        """Create model instance from dictionary."""
        # Convert datetime strings to datetime objects if needed
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class EmbeddingMixin:
    """Mixin for entities that support embedding-based similarity search."""
    
    embedding: Optional[list[float]] = Field(
        default=None, 
        description="Vector embedding for similarity search"
    )
    
    def get_text_for_embedding(self) -> str:
        """
        Get the text representation for embedding generation.
        
        Override in subclasses to specify which fields to include.
        
        Returns:
            Text representation for embedding
        """
        raise NotImplementedError(
            "Subclasses must implement get_text_for_embedding()"
        )