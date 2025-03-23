"""API routes for business object operations."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from src.models.business_object import BusinessObject
from src.repositories.business_object_repo import BusinessObjectRepository
from src.services.embedding_service import embedding_service
from src.utils.errors import NotFoundError, RepositoryError

router = APIRouter()
repo = BusinessObjectRepository()


class BusinessObjectCreateUpdate(BaseModel):
    """Schema for creating or updating a business object."""
    
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    domain: Optional[str] = Field(None, description="Business domain/area")
    steward: Optional[str] = Field(None, description="Data steward responsible")
    criticality: Optional[int] = Field(
        None, ge=1, le=5, description="Business criticality (1-5)"
    )


@router.post(
    "/",
    response_model=BusinessObject,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new business object",
)
async def create_business_object(
    data: BusinessObjectCreateUpdate
) -> BusinessObject:
    """
    Create a new business object in the data catalog.
    
    Args:
        data: Business object data
        
    Returns:
        Created business object
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Generate a unique ID (in production, use a more robust ID generation)
        import uuid
        object_id = f"BO-{uuid.uuid4().hex[:8].upper()}"
        
        # Create business object instance
        business_object = BusinessObject(
            object_id=object_id,
            name=data.name,
            description=data.description,
            domain=data.domain,
            steward=data.steward,
            criticality=data.criticality,
        )
        
        # Generate embedding
        try:
            embedding = embedding_service.generate_entity_embedding(business_object)
            business_object.embedding = embedding
        except Exception as e:
            # Log but continue without embedding
            pass
        
        # Save to database
        created_object = repo.create(business_object)
        return created_object
    except RepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create business object: {str(e)}",
        )


@router.get(
    "/{object_id}",
    response_model=BusinessObject,
    summary="Get a business object by ID",
)
async def get_business_object(
    object_id: str = Path(..., description="Business object ID")
) -> BusinessObject:
    """
    Get a business object by ID.
    
    Args:
        object_id: Business object ID
        
    Returns:
        Business object
        
    Raises:
        HTTPException: If object not found or retrieval fails
    """
    try:
        return repo.get_by_id(object_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business object: {str(e)}",
        )


@router.put(
    "/{object_id}",
    response_model=BusinessObject,
    summary="Update a business object",
)
async def update_business_object(
    data: BusinessObjectCreateUpdate,
    object_id: str = Path(..., description="Business object ID"),
) -> BusinessObject:
    """
    Update an existing business object.
    
    Args:
        data: Updated business object data
        object_id: Business object ID
        
    Returns:
        Updated business object
        
    Raises:
        HTTPException: If object not found or update fails
    """
    try:
        # Get existing object
        existing_object = repo.get_by_id(object_id)
        
        # Update fields
        existing_object.name = data.name
        existing_object.description = data.description
        existing_object.domain = data.domain
        existing_object.steward = data.steward
        existing_object.criticality = data.criticality
        
        # Generate new embedding
        try:
            embedding = embedding_service.generate_entity_embedding(existing_object)
            existing_object.embedding = embedding
        except Exception as e:
            # Log but continue without updating embedding
            pass
        
        # Save changes
        updated_object = repo.update(existing_object)
        return updated_object
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business object: {str(e)}",
        )


@router.delete(
    "/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a business object",
)
async def delete_business_object(
    object_id: str = Path(..., description="Business object ID")
) -> None:
    """
    Delete a business object by ID.
    
    Args:
        object_id: Business object ID
        
    Raises:
        HTTPException: If object not found or deletion fails
    """
    try:
        repo.delete(object_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business object: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[BusinessObject],
    summary="List all business objects",
)
async def list_business_objects(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of objects"),
    offset: int = Query(0, ge=0, description="Number of objects to skip"),
) -> List[BusinessObject]:
    """
    List all business objects with pagination.
    
    Args:
        limit: Maximum number of objects to return
        offset: Number of objects to skip
        
    Returns:
        List of business objects
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        return repo.list_all(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list business objects: {str(e)}",
        )


@router.get(
    "/domain/{domain_id}",
    response_model=List[BusinessObject],
    summary="Get business objects by domain",
)
async def get_business_objects_by_domain(
    domain_id: str = Path(..., description="Domain ID")
) -> List[BusinessObject]:
    """
    Get all business objects in a specific domain.
    
    Args:
        domain_id: Domain ID
        
    Returns:
        List of business objects
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        return repo.get_by_domain(domain_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business objects by domain: {str(e)}",
        )


@router.post(
    "/{object_id}/link-domain/{domain_id}",
    status_code=status.HTTP_200_OK,
    summary="Link business object to domain",
)
async def link_business_object_to_domain(
    object_id: str = Path(..., description="Business object ID"),
    domain_id: str = Path(..., description="Domain ID"),
) -> Dict[str, str]:
    """
    Link a business object to a domain.
    
    Args:
        object_id: Business object ID
        domain_id: Domain ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If linking fails
    """
    try:
        repo.link_to_domain(object_id, domain_id)
        return {
            "message": f"Business object {object_id} linked to domain {domain_id} successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link business object to domain: {str(e)}",
        )