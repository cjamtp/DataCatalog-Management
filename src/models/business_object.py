"""
Business Object model for the data catalog.
"""
from typing import List, Optional

from pydantic import Field

from src.models.base import CatalogEntity, EmbeddingMixin


class BusinessObject(CatalogEntity, EmbeddingMixin):
    """
    Represents a business object in the data catalog.
    
    A business object is a high-level concept representing a business entity
    that contains multiple data elements.
    """
    
    id: str = Field(..., alias="object_id", description="Unique business object ID")
    domain: Optional[str] = Field(None, description="Business domain/area")
    steward: Optional[str] = Field(None, description="Data steward responsible")
    criticality: Optional[int] = Field(
        None, 
        ge=1, 
        le=5, 
        description="Business criticality (1-5)"
    )
    
    def get_text_for_embedding(self) -> str:
        """
        Get text representation for embedding generation.
        
        Returns:
            Text combining name, description, and domain
        """
        parts = [
            f"Name: {self.name}",
            f"Description: {self.description}"
        ]
        
        if self.domain:
            parts.append(f"Domain: {self.domain}")
            
        return " ".join(parts)
    
    class Config:
        populate_by_name = True