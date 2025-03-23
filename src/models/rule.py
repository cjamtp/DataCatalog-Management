"""Rule model for the data catalog."""
from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import Field

from src.models.base import CatalogEntity, EmbeddingMixin


class RuleCategory(str, Enum):
    """Enumeration of rule categories."""
    
    DATA = "data"
    VALIDATION = "validation"
    CALCULATION = "calculation"
    PROCESS = "process"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"


class ObligationLevel(str, Enum):
    """Enumeration of rule obligation levels."""
    
    MANDATORY = "mandatory"
    CONDITIONAL = "conditional"
    OPTIONAL = "optional"


class Rule(CatalogEntity, EmbeddingMixin):
    """
    Represents a business or data rule in the data catalog.
    
    Rules define constraints, calculations, and validations that
    apply to business objects and data elements.
    """
    
    id: str = Field(..., alias="rule_id", description="Unique rule ID")
    category: RuleCategory = Field(..., description="Rule category")
    obligation_level: ObligationLevel = Field(
        ObligationLevel.MANDATORY,
        description="Rule obligation level"
    )
    data_elements: List[str] = Field(
        default_factory=list,
        description="List of data elements this rule applies to"
    )
    conditions: List[str] = Field(
        default_factory=list,
        description="Conditions when this rule applies"
    )
    actions: List[str] = Field(
        default_factory=list,
        description="Required actions"
    )
    exceptions: List[str] = Field(
        default_factory=list,
        description="Exceptions to the rule"
    )
    thresholds: Optional[List[float]] = Field(
        None, 
        description="Numerical limits or thresholds"
    )
    validation_logic: Optional[str] = Field(
        None,
        description="Formal expression of validation logic"
    )
    source_reference: Optional[str] = Field(
        None,
        description="Source document reference"
    )
    effective_date: Optional[date] = Field(
        None,
        description="Date when rule takes effect"
    )
    related_rules: List[str] = Field(
        default_factory=list,
        description="IDs of related or dependent rules"
    )
    
    def get_text_for_embedding(self) -> str:
        """
        Get text representation for embedding generation.
        
        Returns:
            Text combining rule information
        """
        parts = [
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Category: {self.category}",
            f"Obligation: {self.obligation_level}"
        ]
        
        if self.conditions:
            parts.append(f"Conditions: {'; '.join(self.conditions)}")
            
        if self.actions:
            parts.append(f"Actions: {'; '.join(self.actions)}")
            
        if self.validation_logic:
            parts.append(f"Logic: {self.validation_logic}")
            
        return " ".join(parts)
    
    class Config:
        populate_by_name = True