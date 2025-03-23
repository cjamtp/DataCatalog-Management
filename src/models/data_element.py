"""
Data Element model for the data catalog.
"""
from enum import Enum
from typing import Optional

from pydantic import Field

from src.models.base import CatalogEntity, EmbeddingMixin


class DataType(str, Enum):
    """Enumeration of supported data types."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    BINARY = "binary"


class SensitivityLevel(str, Enum):
    """Enumeration of data sensitivity levels."""
    
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"
    PCI = "pci"


class DataElement(CatalogEntity, EmbeddingMixin):
    """
    Represents a data element in the data catalog.
    
    A data element is a specific field or attribute that belongs to a business object.
    """
    
    id: str = Field(..., alias="element_id", description="Unique data element ID")
    technical_name: str = Field(..., description="Technical field name")
    data_type: DataType = Field(..., description="Data type")
    format: Optional[str] = Field(None, description="Format specification")
    domain: Optional[str] = Field(None, description="Value domain or constraints")
    sensitivity_level: SensitivityLevel = Field(
        SensitivityLevel.INTERNAL, 
        description="Data sensitivity classification"
    )
    
    def get_text_for_embedding(self) -> str:
        """
        Get text representation for embedding generation.
        
        Returns:
            Text combining name, description, technical name, and data type
        """
        parts = [
            f"Name: {self.name}",
            f"Technical Name: {self.technical_name}",
            f"Description: {self.description}",
            f"Data Type: {self.data_type}"
        ]
        
        if self.format:
            parts.append(f"Format: {self.format}")
            
        if self.domain:
            parts.append(f"Domain: {self.domain}")
            
        return " ".join(parts)
    
    class Config:
        populate_by_name = True