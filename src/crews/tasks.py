"""CrewAI tasks for data catalog operations."""
from typing import Any, Dict, List, Optional

from crewai import Task
from loguru import logger

from src.services.search_service import search_service
from src.utils.errors import CrewAIError


class TaskFactory:
    """Factory for creating CrewAI tasks."""
    
    @staticmethod
    def create_similarity_search_task(
        agent: Any, query: str, entity_types: Optional[List[str]] = None
    ) -> Task:
        """
        Create a task for performing similarity search across data catalog entities.
        
        Args:
            agent: CrewAI agent
            query: Search query text
            entity_types: Types of entities to search (defaults to all)
            
        Returns:
            CrewAI Task
            
        Raises:
            CrewAIError: If task creation fails
        """
        try:
            entity_types_str = ", ".join(entity_types) if entity_types else "all entity types"
            
            return Task(
                description=f"""
                Perform a similarity search for '{query}' across {entity_types_str}.
                
                1. Analyze the search query to understand the user's intent.
                2. Use the search service to find relevant entities.
                3. For each match, explain why it's relevant to the query.
                4. Identify the most important matches and explain their significance.
                5. Summarize the overall findings and their business implications.
                
                Your output should be a comprehensive analysis, not just a list of matches.
                """,
                agent=agent,
                context={
                    "query": query,
                    "entity_types": entity_types,
                    "search_service": search_service
                }
            )
        except Exception as e:
            logger.error(f"Failed to create similarity search task: {e}")
            raise CrewAIError(f"Failed to create similarity search task: {e}")
    
    @staticmethod
    def create_relationship_analysis_task(
        agent: Any, entity_type: str, entity_id: str, entity_name: str
    ) -> Task:
        """
        Create a task for analyzing relationships between data catalog entities.
        
        Args:
            agent: CrewAI agent
            entity_type: Type of entity to analyze
            entity_id: ID of the entity
            entity_name: Name of the entity for human-readable output
            
        Returns:
            CrewAI Task
            
        Raises:
            CrewAIError: If task creation fails
        """
        try:
            readable_type = {
                "business_object": "Business Object",
                "data_element": "Data Element",
                "domain": "Domain",
                "rule": "Rule"
            }.get(entity_type, entity_type)
            
            return Task(
                description=f"""
                Analyze the relationships for {readable_type} '{entity_name}' (ID: {entity_id}).
                
                1. Identify all related entities across all entity types.
                2. Analyze the nature of each relationship.
                3. Explain the significance of key relationships.
                4. Identify any potential issues or gaps in the relationships.
                5. Suggest improvements to strengthen the entity's connections.
                6. Create a narrative about this entity's role in the data landscape.
                
                Provide a comprehensive analysis that helps understand this entity's
                place in the broader data ecosystem.
                """,
                agent=agent,
                context={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "search_service": search_service
                }
            )
        except Exception as e:
            logger.error(f"Failed to create relationship analysis task: {e}")
            raise CrewAIError(f"Failed to create relationship analysis task: {e}")
    
    @staticmethod
    def create_data_quality_assessment_task(
        agent: Any, entity_type: str, entity_id: str, entity_name: str
    ) -> Task:
        """
        Create a task for assessing data quality and governance for an entity.
        
        Args:
            agent: CrewAI agent
            entity_type: Type of entity to assess
            entity_id: ID of the entity
            entity_name: Name of the entity for human-readable output
            
        Returns:
            CrewAI Task
            
        Raises:
            CrewAIError: If task creation fails
        """
        try:
            readable_type = {
                "business_object": "Business Object",
                "data_element": "Data Element",
                "domain": "Domain",
                "rule": "Rule"
            }.get(entity_type, entity_type)
            
            return Task(
                description=f"""
                Assess the data quality and governance aspects of {readable_type} '{entity_name}' (ID: {entity_id}).
                
                1. Analyze the metadata completeness and accuracy.
                2. Review associated business rules and their enforcement.
                3. Identify potential data quality issues or risks.
                4. Evaluate compliance with governance standards.
                5. Recommend specific improvements to enhance data quality.
                6. Provide an overall quality and governance score with justification.
                
                Your assessment should be balanced, highlighting both strengths and areas for improvement.
                """,
                agent=agent,
                context={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "search_service": search_service
                }
            )
        except Exception as e:
            logger.error(f"Failed to create data quality assessment task: {e}")
            raise CrewAIError(f"Failed to create data quality assessment task: {e}")
    
    @staticmethod
    def create_metadata_enhancement_task(
        agent: Any, entity_type: str, entity_id: str, entity_name: str
    ) -> Task:
        """
        Create a task for suggesting metadata enhancements for an entity.
        
        Args:
            agent: CrewAI agent
            entity_type: Type of entity to enhance
            entity_id: ID of the entity
            entity_name: Name of the entity for human-readable output
            
        Returns:
            CrewAI Task
            
        Raises:
            CrewAIError: If task creation fails
        """
        try:
            readable_type = {
                "business_object": "Business Object",
                "data_element": "Data Element",
                "domain": "Domain",
                "rule": "Rule"
            }.get(entity_type, entity_type)
            
            return Task(
                description=f"""
                Suggest metadata enhancements for {readable_type} '{entity_name}' (ID: {entity_id}).
                
                1. Review the current metadata for completeness and clarity.
                2. Identify missing or unclear metadata elements.
                3. Suggest improvements to the entity's name and description.
                4. Recommend additional context that would make the entity more discoverable.
                5. Propose business glossary terms that should be associated with this entity.
                6. Suggest classification tags or categories to improve organization.
                
                Provide specific suggestions with clear rationales for each enhancement.
                """,
                agent=agent,
                context={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "search_service": search_service
                }
            )
        except Exception as e:
            logger.error(f"Failed to create metadata enhancement task: {e}")
            raise CrewAIError(f"Failed to create metadata enhancement task: {e}")
    
    @staticmethod
    def create_rule_analysis_task(
        agent: Any, rule_id: str, rule_name: str
    ) -> Task:
        """
        Create a task for analyzing a business rule and its implications.
        
        Args:
            agent: CrewAI agent
            rule_id: ID of the rule
            rule_name: Name of the rule for human-readable output
            
        Returns:
            CrewAI Task
            
        Raises:
            CrewAIError: If task creation fails
        """
        try:
            return Task(
                description=f"""
                Analyze Business Rule '{rule_name}' (ID: {rule_id}) and its implications.
                
                1. Interpret the rule's intent and business purpose.
                2. Identify all data elements governed by this rule.
                3. Explain how this rule ensures data quality or compliance.
                4. Analyze relationships with other rules (conflicts, dependencies).
                5. Identify potential implementation challenges.
                6. Suggest clarifications or improvements to the rule definition.
                
                Provide a comprehensive analysis that helps stakeholders understand
                the rule's importance and impact on the data landscape.
                """,
                agent=agent,
                context={
                    "rule_id": rule_id,
                    "rule_name": rule_name,
                    "search_service": search_service
                }
            )
        except Exception as e:
            logger.error(f"Failed to create rule analysis task: {e}")
            raise CrewAIError(f"Failed to create rule analysis task: {e}")


# Easy access functions for tasks
def create_similarity_search_task(agent: Any, query: str, entity_types: Optional[List[str]] = None) -> Task:
    """Create a similarity search task."""
    return TaskFactory.create_similarity_search_task(agent, query, entity_types)

def create_relationship_analysis_task(agent: Any, entity_type: str, entity_id: str, entity_name: str) -> Task:
    """Create a relationship analysis task."""
    return TaskFactory.create_relationship_analysis_task(agent, entity_type, entity_id, entity_name)

def create_data_quality_assessment_task(agent: Any, entity_type: str, entity_id: str, entity_name: str) -> Task:
    """Create a data quality assessment task."""
    return TaskFactory.create_data_quality_assessment_task(agent, entity_type, entity_id, entity_name)

def create_metadata_enhancement_task(agent: Any, entity_type: str, entity_id: str, entity_name: str) -> Task:
    """Create a metadata enhancement task."""
    return TaskFactory.create_metadata_enhancement_task(agent, entity_type, entity_id, entity_name)

def create_rule_analysis_task(agent: Any, rule_id: str, rule_name: str) -> Task:
    """Create a rule analysis task."""
    return TaskFactory.create_rule_analysis_task(agent, rule_id, rule_name)