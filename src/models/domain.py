"""
Domain model for the data catalog.
"""
from enum import Enum
from typing import Optional

from pydantic import Field

from src.models.base import CatalogEntity, EmbeddingMixin


class MaturityLevel(str, Enum):
    """Enumeration of domain maturity levels."""
    
    INITIAL = "initial"
    DEVELOPING = "developing"
    DEFINED = "defined"
    MANAGED = "managed"
    OPTIMIZED = "optimized"


class Domain(CatalogEntity, EmbeddingMixin):
    """
    Represents a business domain in the data catalog.
    
    A domain is a business area or subject area that provides context
    for business objects and rules.
    """
    
    id: str = Field(..., alias="domain_id", description="Unique domain ID")
    owner: str = Field(..., description="Domain owner (person or team)")
    steward: Optional[str] = Field(None, description="Domain steward")
    parent_domain_id: Optional[str] = Field(
        None, 
        description="Parent domain ID for hierarchical domains"
    )
    maturity_level: MaturityLevel = Field(
        MaturityLevel.INITIAL,
        description="Domain governance maturity level"
    )
    strategic_priority: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Strategic priority (1-5)"
    )
    data_classification_policy: Optional[str] = Field(
        None,
        description="Default data classification policy"
    )
    
    def get_text_for_embedding(self) -> str:
        """
        Get text representation for embedding generation.
        
        Returns:
            Text combining name, description, and policy info
        """
        parts = [
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Owner: {self.owner}"
        ]
        
        if self.data_classification_policy:
            parts.append(f"Policy: {self.data_classification_policy}")
            
        return " ".join(parts)
    
    class Config:
        populate_by_name = True