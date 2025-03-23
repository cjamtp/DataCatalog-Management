"""API routes for rule operations."""
from datetime import date
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from src.models.rule import ObligationLevel, Rule, RuleCategory
from src.repositories.rule_repo import RuleRepository
from src.services.embedding_service import embedding_service
from src.utils.errors import NotFoundError, RepositoryError

router = APIRouter()
repo = RuleRepository()


class RuleCreateUpdate(BaseModel):
    """Schema for creating or updating a rule."""
    
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    category: RuleCategory = Field(..., description="Rule category")
    obligation_level: ObligationLevel = Field(
        ObligationLevel.MANDATORY, description="Rule obligation level"
    )
    data_elements: List[str] = Field(
        default_factory=list, description="Data elements this rule applies to"
    )
    conditions: List[str] = Field(
        default_factory=list, description="Conditions when this rule applies"
    )
    actions: List[str] = Field(
        default_factory=list, description="Required actions"
    )
    exceptions: List[str] = Field(
        default_factory=list, description="Exceptions to the rule"
    )
    thresholds: Optional[List[float]] = Field(
        None, description="Numerical limits or thresholds"
    )
    validation_logic: Optional[str] = Field(
        None, description="Formal expression of validation logic"
    )
    source_reference: Optional[str] = Field(
        None, description="Source document reference"
    )
    effective_date: Optional[date] = Field(
        None, description="Date when rule takes effect"
    )
    related_rules: List[str] = Field(
        default_factory=list, description="IDs of related or dependent rules"
    )


@router.post(
    "/",
    response_model=Rule,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new rule",
)
async def create_rule(data: RuleCreateUpdate) -> Rule:
    """
    Create a new rule in the data catalog.
    
    Args:
        data: Rule data
        
    Returns:
        Created rule
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Generate a unique ID (in production, use a more robust ID generation)
        import uuid
        rule_id = f"R-{uuid.uuid4().hex[:8].upper()}"
        
        # Create rule instance
        rule = Rule(
            rule_id=rule_id,
            name=data.name,
            description=data.description,
            category=data.category,
            obligation_level=data.obligation_level,
            data_elements=data.data_elements,
            conditions=data.conditions,
            actions=data.actions,
            exceptions=data.exceptions,
            thresholds=data.thresholds,
            validation_logic=data.validation_logic,
            source_reference=data.source_reference,
            effective_date=data.effective_date,
            related_rules=data.related_rules,
        )
        
        # Generate embedding
        try:
            embedding = embedding_service.generate_entity_embedding(rule)
            rule.embedding = embedding
        except Exception as e:
            # Log but continue without embedding
            pass
        
        # Save to database
        created_rule = repo.create(rule)
        return created_rule
    except RepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}",
        )


@router.get(
    "/{rule_id}",
    response_model=Rule,
    summary="Get a rule by ID",
)
async def get_rule(
    rule_id: str = Path(..., description="Rule ID")
) -> Rule:
    """
    Get a rule by ID.
    
    Args:
        rule_id: Rule ID
        
    Returns:
        Rule
        
    Raises:
        HTTPException: If rule not found or retrieval fails
    """
    try:
        return repo.get_by_id(rule_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rule: {str(e)}",
        )


@router.put(
    "/{rule_id}",
    response_model=Rule,
    summary="Update a rule",
)
async def update_rule(
    data: RuleCreateUpdate,
    rule_id: str = Path(..., description="Rule ID"),
) -> Rule:
    """
    Update an existing rule.
    
    Args:
        data: Updated rule data
        rule_id: Rule ID
        
    Returns:
        Updated rule
        
    Raises:
        HTTPException: If rule not found or update fails
    """
    try:
        # Get existing rule
        existing_rule = repo.get_by_id(rule_id)
        
        # Update fields
        existing_rule.name = data.name
        existing_rule.description = data.description
        existing_rule.category = data.category
        existing_rule.obligation_level = data.obligation_level
        existing_rule.data_elements = data.data_elements
        existing_rule.conditions = data.conditions
        existing_rule.actions = data.actions
        existing_rule.exceptions = data.exceptions
        existing_rule.thresholds = data.thresholds
        existing_rule.validation_logic = data.validation_logic
        existing_rule.source_reference = data.source_reference
        existing_rule.effective_date = data.effective_date
        existing_rule.related_rules = data.related_rules
        
        # Generate new embedding
        try:
            embedding = embedding_service.generate_entity_embedding(existing_rule)
            existing_rule.embedding = embedding
        except Exception as e:
            # Log but continue without updating embedding
            pass
        
        # Save changes
        updated_rule = repo.update(existing_rule)
        return updated_rule
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}",
        )


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a rule",
)
async def delete_rule(
    rule_id: str = Path(..., description="Rule ID")
) -> None:
    """
    Delete a rule by ID.
    
    Args:
        rule_id: Rule ID
        
    Raises:
        HTTPException: If rule not found or deletion fails
    """
    try:
        repo.delete(rule_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[Rule],
    summary="List all rules",
)
async def list_rules(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of rules"),
    offset: int = Query(0, ge=0, description="Number of rules to skip"),
) -> List[Rule]:
    """
    List all rules with pagination.
    
    Args:
        limit: Maximum number of rules to return
        offset: Number of rules to skip
        
    Returns:
        List of rules
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        return repo.list_all(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rules: {str(e)}",
        )


@router.get(
    "/category/{category}",
    response_model=List[Rule],
    summary="Get rules by category",
)
async def get_rules_by_category(
    category: RuleCategory = Path(..., description="Rule category")
) -> List[Rule]:
    """
    Get all rules in a specific category.
    
    Args:
        category: Rule category
        
    Returns:
        List of rules
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return repo.get_by_category(category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rules by category: {str(e)}",
        )


@router.get(
    "/{rule_id}/related",
    response_model=List[Rule],
    summary="Get related rules",
)
async def get_related_rules(
    rule_id: str = Path(..., description="Rule ID")
) -> List[Rule]:
    """
    Get rules related to a specific rule.
    
    Args:
        rule_id: Rule ID
        
    Returns:
        List of related rules
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return repo.get_related_rules(rule_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get related rules: {str(e)}",
        )