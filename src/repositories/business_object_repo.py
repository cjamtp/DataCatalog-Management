"""Repository for business object operations."""
import json
from typing import Dict, List, Optional, Union

from loguru import logger

from src.db.neo4j_client import neo4j_client
from src.models.business_object import BusinessObject
from src.utils.errors import NotFoundError, RepositoryError


class BusinessObjectRepository:
    """Repository for business object CRUD operations."""
    
    def create(self, business_object: BusinessObject) -> BusinessObject:
        """
        Create a new business object in the database.
        
        Args:
            business_object: BusinessObject instance to create
            
        Returns:
            Created BusinessObject with updated metadata
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Prepare parameters
            params = business_object.to_dict()
            
            # Convert datetime objects to ISO format strings
            if "created_at" in params:
                params["created_at"] = params["created_at"].isoformat()
            if "updated_at" in params:
                params["updated_at"] = params["updated_at"].isoformat()
                
            # Handle embedding separately if present
            embedding = None
            if "embedding" in params and params["embedding"] is not None:
                embedding = params.pop("embedding")
                
            query = """
            CREATE (bo:BusinessObject $params)
            RETURN bo
            """
            
            # Execute query
            result = neo4j_client.execute_query(query, {"params": params})
            
            if not result:
                raise RepositoryError("Failed to create business object")
                
            # Add embedding if available
            if embedding:
                embedding_query = """
                MATCH (bo:BusinessObject {object_id: $object_id})
                SET bo.embedding = $embedding
                RETURN bo
                """
                neo4j_client.execute_query(
                    embedding_query, 
                    {"object_id": business_object.id, "embedding": json.dumps(embedding)}
                )
                
            # Return created object
            created_obj = BusinessObject.from_dict(result[0]["bo"])
            
            logger.info(f"Created business object: {created_obj.id}")
            return created_obj
            
        except Exception as e:
            logger.error(f"Failed to create business object: {e}")
            raise RepositoryError(f"Failed to create business object: {e}")
    
    def get_by_id(self, object_id: str) -> BusinessObject:
        """
        Get a business object by ID.
        
        Args:
            object_id: Business object ID
            
        Returns:
            BusinessObject instance
            
        Raises:
            NotFoundError: If object not found
            RepositoryError: If retrieval fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject {object_id: $object_id})
            RETURN bo
            """
            
            result = neo4j_client.execute_query(query, {"object_id": object_id})
            
            if not result:
                raise NotFoundError(f"Business object not found: {object_id}")
                
            # Handle embedding conversion from JSON string if present
            bo_data = result[0]["bo"]
            if "embedding" in bo_data and isinstance(bo_data["embedding"], str):
                bo_data["embedding"] = json.loads(bo_data["embedding"])
                
            return BusinessObject.from_dict(bo_data)
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get business object: {e}")
            raise RepositoryError(f"Failed to get business object: {e}")
    
    def update(self, business_object: BusinessObject) -> BusinessObject:
        """
        Update an existing business object.
        
        Args:
            business_object: BusinessObject with updated values
            
        Returns:
            Updated BusinessObject
            
        Raises:
            NotFoundError: If object not found
            RepositoryError: If update fails
        """
        try:
            # Check if object exists
            self.get_by_id(business_object.id)
            
            # Prepare parameters
            params = business_object.to_dict()
            
            # Convert datetime objects to ISO format strings
            if "created_at" in params:
                params["created_at"] = params["created_at"].isoformat()
            if "updated_at" in params:
                params["updated_at"] = params["updated_at"].isoformat()
                
            # Handle embedding separately if present
            embedding = None
            if "embedding" in params and params["embedding"] is not None:
                embedding = params.pop("embedding")
            
            query = """
            MATCH (bo:BusinessObject {object_id: $object_id})
            SET bo = $params
            RETURN bo
            """
            
            result = neo4j_client.execute_query(
                query, {"object_id": business_object.id, "params": params}
            )
            
            # Update embedding if available
            if embedding:
                embedding_query = """
                MATCH (bo:BusinessObject {object_id: $object_id})
                SET bo.embedding = $embedding
                RETURN bo
                """
                neo4j_client.execute_query(
                    embedding_query, 
                    {"object_id": business_object.id, "embedding": json.dumps(embedding)}
                )
            
            logger.info(f"Updated business object: {business_object.id}")
            
            # Return updated object
            updated_obj = BusinessObject.from_dict(result[0]["bo"])
            updated_obj.embedding = embedding  # Restore embedding if it was set
            return updated_obj
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update business object: {e}")
            raise RepositoryError(f"Failed to update business object: {e}")
    
    def delete(self, object_id: str) -> bool:
        """
        Delete a business object by ID.
        
        Args:
            object_id: Business object ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If object not found
            RepositoryError: If deletion fails
        """
        try:
            # Check if object exists
            self.get_by_id(object_id)
            
            # Delete the object and all its relationships
            query = """
            MATCH (bo:BusinessObject {object_id: $object_id})
            DETACH DELETE bo
            """
            
            neo4j_client.execute_query(query, {"object_id": object_id})
            
            logger.info(f"Deleted business object: {object_id}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete business object: {e}")
            raise RepositoryError(f"Failed to delete business object: {e}")
    
    def list_all(self, limit: int = 100, offset: int = 0) -> List[BusinessObject]:
        """
        List all business objects with pagination.
        
        Args:
            limit: Maximum number of objects to return
            offset: Number of objects to skip
            
        Returns:
            List of BusinessObject instances
            
        Raises:
            RepositoryError: If listing fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject)
            RETURN bo
            ORDER BY bo.name
            SKIP $offset
            LIMIT $limit
            """
            
            result = neo4j_client.execute_query(
                query, {"offset": offset, "limit": limit}
            )
            
            objects = []
            for record in result:
                bo_data = record["bo"]
                if "embedding" in bo_data and isinstance(bo_data["embedding"], str):
                    bo_data["embedding"] = json.loads(bo_data["embedding"])
                objects.append(BusinessObject.from_dict(bo_data))
                
            return objects
            
        except Exception as e:
            logger.error(f"Failed to list business objects: {e}")
            raise RepositoryError(f"Failed to list business objects: {e}")
    
    def get_by_domain(self, domain_id: str) -> List[BusinessObject]:
        """
        Get all business objects in a specific domain.
        
        Args:
            domain_id: Domain ID
            
        Returns:
            List of BusinessObject instances
            
        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject)-[:BELONGS_TO]->(d:Domain {domain_id: $domain_id})
            RETURN bo
            """
            
            result = neo4j_client.execute_query(query, {"domain_id": domain_id})
            
            objects = []
            for record in result:
                bo_data = record["bo"]
                if "embedding" in bo_data and isinstance(bo_data["embedding"], str):
                    bo_data["embedding"] = json.loads(bo_data["embedding"])
                objects.append(BusinessObject.from_dict(bo_data))
                
            return objects
            
        except Exception as e:
            logger.error(f"Failed to get business objects by domain: {e}")
            raise RepositoryError(f"Failed to get business objects by domain: {e}")
    
    def link_to_domain(self, object_id: str, domain_id: str) -> bool:
        """
        Link a business object to a domain.
        
        Args:
            object_id: Business object ID
            domain_id: Domain ID
            
        Returns:
            True if linked successfully
            
        Raises:
            NotFoundError: If object or domain not found
            RepositoryError: If linking fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject {object_id: $object_id})
            MATCH (d:Domain {domain_id: $domain_id})
            MERGE (bo)-[:BELONGS_TO]->(d)
            RETURN bo, d
            """
            
            result = neo4j_client.execute_query(
                query, {"object_id": object_id, "domain_id": domain_id}
            )
            
            if not result:
                raise RepositoryError("Failed to link business object to domain")
                
            logger.info(f"Linked business object {object_id} to domain {domain_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to link business object to domain: {e}")
            raise RepositoryError(f"Failed to link business object to domain: {e}")
    
    def get_all_with_embeddings(self) -> List[Dict]:
        """
        Get all business objects with their embeddings for similarity search.
        
        Returns:
            List of dictionaries containing object ID, name, and embedding
            
        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject)
            WHERE bo.embedding IS NOT NULL
            RETURN bo.object_id AS id, bo.name AS name, bo.embedding AS embedding
            """
            
            result = neo4j_client.execute_query(query)
            
            # Parse embeddings from JSON strings
            for item in result:
                if isinstance(item["embedding"], str):
                    item["embedding"] = json.loads(item["embedding"])
                    
            return result
            
        except Exception as e:
            logger.error(f"Failed to get business objects with embeddings: {e}")
            raise RepositoryError(f"Failed to get objects with embeddings: {e}")
    
    def get_by_data_element(self, element_id: str) -> Optional[BusinessObject]:
        """
        Get the business object that contains a specific data element.
        
        Args:
            element_id: Data element ID
            
        Returns:
            BusinessObject instance or None if not found
            
        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            query = """
            MATCH (bo:BusinessObject)-[:CONTAINS]->(de:DataElement {element_id: $element_id})
            RETURN bo
            """
            
            result = neo4j_client.execute_query(query, {"element_id": element_id})
            
            if not result:
                return None
                
            bo_data = result[0]["bo"]
            if "embedding" in bo_data and isinstance(bo_data["embedding"], str):
                bo_data["embedding"] = json.loads(bo_data["embedding"])
                
            return BusinessObject.from_dict(bo_data)
            
        except Exception as e:
            logger.error(f"Failed to get business object by data element: {e}")
            raise RepositoryError(f"Failed to get business object by data element: {e}")
