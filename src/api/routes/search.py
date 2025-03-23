"""API routes for search operations."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from src.services.search_service import search_service
from src.utils.errors import SearchError

router = APIRouter()


class EntitySearchResult(BaseModel):
    """Schema for entity search result."""
    
    id: str = Field(..., description="Entity ID")
    name: str = Field(..., description="Entity name")
    similarity: float = Field(..., description="Similarity score")


class SearchResults(BaseModel):
    """Schema for search results."""
    
    business_objects: Optional[List[EntitySearchResult]] = Field(
        default=[], description="Business object results"
    )
    data_elements: Optional[List[EntitySearchResult]] = Field(
        default=[], description="Data element results"
    )
    domains: Optional[List[EntitySearchResult]] = Field(
        default=[], description="Domain results"
    )
    rules: Optional[List[EntitySearchResult]] = Field(
        default=[], description="Rule results"
    )


class RelatedEntity(BaseModel):
    """Schema for related entity."""
    
    id: str = Field(..., description="Entity ID")
    name: str = Field(..., description="Entity name")


class RelatedEntities(BaseModel):
    """Schema for related entities."""
    
    business_objects: Optional[List[RelatedEntity]] = Field(
        default=[], description="Related business objects"
    )
    data_elements: Optional[List[RelatedEntity]] = Field(
        default=[], description="Related data elements"
    )
    domains: Optional[List[RelatedEntity]] = Field(
        default=[], description="Related domains"
    )
    rules: Optional[List[RelatedEntity]] = Field(
        default=[], description="Related rules"
    )
    related_rules: Optional[List[RelatedEntity]] = Field(
        default=[], description="Related rules (for rule entities)"
    )


@router.get(
    "/similarity",
    response_model=SearchResults,
    summary="Search entities by text similarity",
)
async def search_by_similarity(
    query: str = Query(..., description="Search query text"),
    types: Optional[List[str]] = Query(
        None,
        description="Entity types to search (business_object, data_element, domain, rule)",
    ),
    threshold: float = Query(
        0.7, ge=0, le=1, description="Minimum similarity threshold"
    ),
    limit: int = Query(5, ge=1, le=20, description="Maximum results per entity type"),
) -> SearchResults:
    """
    Search for entities by text similarity.
    
    Args:
        query: Search query text
        types: Entity types to search
        threshold: Minimum similarity threshold
        limit: Maximum results per entity type
        
    Returns:
        Search results grouped by entity type
        
    Raises:
        HTTPException: If search fails
    """
    try:
        # Validate entity types
        valid_types = ["business_object", "data_element", "domain", "rule"]
        if types:
            for t in types:
                if t not in valid_types:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid entity type: {t}. Valid types are {valid_types}",
                    )
        
        # Perform search
        results = search_service.search_by_text(query, types)
        
        # Convert to response model
        response = SearchResults(
            business_objects=results.get("business_objects", []),
            data_elements=results.get("data_elements", []),
            domains=results.get("domains", []),
            rules=results.get("rules", []),
        )
        
        return response
    except SearchError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.get(
    "/related/{entity_type}/{entity_id}",
    response_model=RelatedEntities,
    summary="Find related entities",
)
async def find_related_entities(
    entity_type: str = Path(
        ..., description="Entity type (business_object, data_element, domain, rule)"
    ),
    entity_id: str = Path(..., description="Entity ID"),
) -> RelatedEntities:
    """
    Find entities related to a specific entity.
    
    Args:
        entity_type: Entity type
        entity_id: Entity ID
        
    Returns:
        Related entities grouped by type
        
    Raises:
        HTTPException: If search fails
    """
    try:
        # Validate entity type
        valid_types = ["business_object", "data_element", "domain", "rule"]
        if entity_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity type: {entity_type}. Valid types are {valid_types}",
            )
        
        # Find related entities
        results = search_service.find_related_entities(entity_type, entity_id)
        
        # Convert to response model
        response = RelatedEntities(
            business_objects=results.get("business_objects", []),
            data_elements=results.get("data_elements", []),
            domains=results.get("domains", []),
            rules=results.get("rules", []),
            related_rules=results.get("related_rules", []),
        )
        
        return response
    except SearchError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find related entities: {str(e)}",
        )