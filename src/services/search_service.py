"""Service for searching across different catalog entities."""
from typing import Dict, List, Optional, Union

from loguru import logger

from src.repositories.business_object_repo import BusinessObjectRepository
from src.repositories.data_element_repo import DataElementRepository
from src.repositories.domain_repo import DomainRepository
from src.repositories.rule_repo import RuleRepository
from src.services.embedding_service import embedding_service
from src.utils.errors import SearchError


class SearchService:
    """Service for searching across data catalog entities."""
    
    def __init__(self):
        """Initialize repositories."""
        self.business_object_repo = BusinessObjectRepository()
        self.data_element_repo = DataElementRepository()
        self.domain_repo = DomainRepository()
        self.rule_repo = RuleRepository()
    
    def search_by_text(self, query: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Search for entities by text similarity.
        
        Args:
            query: Search query text
            entity_types: List of entity types to search (defaults to all)
            
        Returns:
            Dictionary with entity types as keys and lists of search results as values
            
        Raises:
            SearchError: If search fails
        """
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Default to all entity types if not specified
            if not entity_types:
                entity_types = ["business_object", "data_element", "domain", "rule"]
                
            results = {}
            
            # Search business objects
            if "business_object" in entity_types:
                bo_embeddings = self.business_object_repo.get_all_with_embeddings()
                bo_results = embedding_service.find_similar_entities(
                    query_embedding, bo_embeddings
                )
                results["business_objects"] = bo_results
                
            # Search data elements
            if "data_element" in entity_types:
                de_embeddings = self.data_element_repo.get_all_with_embeddings()
                de_results = embedding_service.find_similar_entities(
                    query_embedding, de_embeddings
                )
                results["data_elements"] = de_results
                
            # Search domains
            if "domain" in entity_types:
                domain_embeddings = self.domain_repo.get_all_with_embeddings()
                domain_results = embedding_service.find_similar_entities(
                    query_embedding, domain_embeddings
                )
                results["domains"] = domain_results
                
            # Search rules
            if "rule" in entity_types:
                rule_embeddings = self.rule_repo.get_all_with_embeddings()
                rule_results = embedding_service.find_similar_entities(
                    query_embedding, rule_embeddings
                )
                results["rules"] = rule_results
                
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}")
    
    def find_related_entities(
        self, entity_type: str, entity_id: str
    ) -> Dict[str, List[Dict]]:
        """
        Find entities related to a specific entity.
        
        Args:
            entity_type: Type of the entity (business_object, data_element, domain, rule)
            entity_id: ID of the entity
            
        Returns:
            Dictionary with entity types as keys and lists of related entities as values
            
        Raises:
            SearchError: If search fails
        """
        try:
            results = {}
            
            if entity_type == "business_object":
                # Find data elements contained in this business object
                data_elements = self.data_element_repo.get_by_business_object(entity_id)
                results["data_elements"] = [
                    {"id": de.id, "name": de.name} for de in data_elements
                ]
                
                # Find domain this business object belongs to
                domain = self.domain_repo.get_by_business_object(entity_id)
                if domain:
                    results["domains"] = [{"id": domain.id, "name": domain.name}]
                
            elif entity_type == "data_element":
                # Find business object containing this data element
                business_object = self.business_object_repo.get_by_data_element(entity_id)
                if business_object:
                    results["business_objects"] = [
                        {"id": business_object.id, "name": business_object.name}
                    ]
                
                # Find rules governing this data element
                rules = self.rule_repo.get_by_data_element(entity_id)
                results["rules"] = [{"id": rule.id, "name": rule.name} for rule in rules]
                
            elif entity_type == "domain":
                # Find business objects in this domain
                business_objects = self.business_object_repo.get_by_domain(entity_id)
                results["business_objects"] = [
                    {"id": bo.id, "name": bo.name} for bo in business_objects
                ]
                
                # Find rules enforced by this domain
                rules = self.rule_repo.get_by_domain(entity_id)
                results["rules"] = [{"id": rule.id, "name": rule.name} for rule in rules]
                
            elif entity_type == "rule":
                # Find data elements governed by this rule
                data_elements = self.data_element_repo.get_by_rule(entity_id)
                results["data_elements"] = [
                    {"id": de.id, "name": de.name} for de in data_elements
                ]
                
                # Find domains enforcing this rule
                domains = self.domain_repo.get_by_rule(entity_id)
                results["domains"] = [
                    {"id": domain.id, "name": domain.name} for domain in domains
                ]
                
                # Find related rules
                rule = self.rule_repo.get_by_id(entity_id)
                if rule and rule.related_rules:
                    related_rules = []
                    for related_id in rule.related_rules:
                        try:
                            related_rule = self.rule_repo.get_by_id(related_id)
                            related_rules.append({
                                "id": related_rule.id,
                                "name": related_rule.name
                            })
                        except Exception:
                            # Skip rules that can't be found
                            pass
                    results["related_rules"] = related_rules
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to find related entities: {e}")
            raise SearchError(f"Failed to find related entities: {e}")


# Global search service instance
search_service = SearchService()