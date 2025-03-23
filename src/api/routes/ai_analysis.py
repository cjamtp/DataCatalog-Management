"""API routes for AI-powered analysis using CrewAI."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from src.crews.crew import run_entity_analysis, run_rule_analysis, run_similarity_search
from src.utils.errors import CrewAIError

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Schema for an AI analysis request."""
    
    query: str = Field(..., description="Analysis query text")
    entity_types: Optional[List[str]] = Field(
        None, description="Entity types to include in analysis"
    )


class AnalysisResponse(BaseModel):
    """Schema for an AI analysis response."""
    
    result: str = Field(..., description="Analysis result")


@router.post(
    "/similarity-search",
    response_model=AnalysisResponse,
    summary="Perform AI-powered similarity search",
)
async def similarity_search(request: AnalysisRequest) -> AnalysisResponse:
    """
    Perform an AI-powered similarity search across catalog entities.
    
    Args:
        request: Analysis request
        
    Returns:
        Analysis result
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Validate entity types if provided
        valid_types = ["business_object", "data_element", "domain", "rule"]
        if request.entity_types:
            for t in request.entity_types:
                if t not in valid_types:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid entity type: {t}. Valid types are {valid_types}",
                    )
        
        # Run analysis
        result = run_similarity_search(request.query, request.entity_types)
        
        return AnalysisResponse(result=result)
    except CrewAIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )


@router.post(
    "/entity-analysis/{entity_type}/{entity_id}/{entity_name}",
    response_model=AnalysisResponse,
    summary="Perform AI-powered entity analysis",
)
async def entity_analysis(
    entity_type: str = Path(
        ..., description="Entity type (business_object, data_element, domain, rule)"
    ),
    entity_id: str = Path(..., description="Entity ID"),
    entity_name: str = Path(..., description="Entity name"),
) -> AnalysisResponse:
    """
    Perform an AI-powered analysis of a specific entity.
    
    Args:
        entity_type: Type of entity to analyze
        entity_id: ID of the entity
        entity_name: Name of the entity
        
    Returns:
        Analysis result
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Validate entity type
        valid_types = ["business_object", "data_element", "domain", "rule"]
        if entity_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity type: {entity_type}. Valid types are {valid_types}",
            )
        
        # Run analysis
        result = run_entity_analysis(entity_type, entity_id, entity_name)
        
        return AnalysisResponse(result=result)
    except CrewAIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )


@router.post(
    "/rule-analysis/{rule_id}/{rule_name}",
    response_model=AnalysisResponse,
    summary="Perform AI-powered rule analysis",
)
async def rule_analysis(
    rule_id: str = Path(..., description="Rule ID"),
    rule_name: str = Path(..., description="Rule name"),
) -> AnalysisResponse:
    """
    Perform an AI-powered analysis of a specific rule.
    
    Args:
        rule_id: ID of the rule
        rule_name: Name of the rule
        
    Returns:
        Analysis result
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Run analysis
        result = run_rule_analysis(rule_id, rule_name)
        
        return AnalysisResponse(result=result)
    except CrewAIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}",
        )