"""CrewAI crew for data catalog operations."""
from typing import Any, Dict, List, Optional

from crewai import Crew, Process, Task
from loguru import logger

from src.crews.agents import (get_business_analyst_agent, get_data_explorer_agent,
                             get_data_steward_agent, get_metadata_expert_agent)
from src.crews.tasks import (create_data_quality_assessment_task,
                            create_metadata_enhancement_task,
                            create_relationship_analysis_task,
                            create_rule_analysis_task,
                            create_similarity_search_task)
from src.utils.errors import CrewAIError


class DataCatalogCrew:
    """Crew for data catalog operations."""
    
    def __init__(self):
        """Initialize agents for the crew."""
        self.data_explorer = get_data_explorer_agent()
        self.business_analyst = get_business_analyst_agent()
        self.data_steward = get_data_steward_agent()
        self.metadata_expert = get_metadata_expert_agent()
    
    def similarity_search_crew(self, query: str, entity_types: Optional[List[str]] = None) -> Crew:
        """
        Create a crew for similarity search operations.
        
        Args:
            query: Search query text
            entity_types: Types of entities to search
            
        Returns:
            CrewAI Crew
            
        Raises:
            CrewAIError: If crew creation fails
        """
        try:
            # Create tasks
            search_task = create_similarity_search_task(
                self.data_explorer, query, entity_types
            )
            analyze_task = Task(
                description=f"""
                Based on the search results for '{query}', provide business context
                and implications for the most relevant matches.
                
                1. Analyze the top search results from the data explorer.
                2. Explain the business significance of these matches.
                3. Identify potential use cases or insights from these entities.
                4. Highlight any governance or compliance considerations.
                
                Your analysis should provide valuable business context that enhances
                the technical search results.
                """,
                agent=self.business_analyst,
                context={"query": query}
            )
            
            # Create crew
            return Crew(
                agents=[self.data_explorer, self.business_analyst],
                tasks=[search_task, analyze_task],
                process=Process.sequential,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Failed to create similarity search crew: {e}")
            raise CrewAIError(f"Failed to create similarity search crew: {e}")
    
    def entity_analysis_crew(
        self, entity_type: str, entity_id: str, entity_name: str
    ) -> Crew:
        """
        Create a crew for comprehensive entity analysis.
        
        Args:
            entity_type: Type of entity to analyze
            entity_id: ID of the entity
            entity_name: Name of the entity
            
        Returns:
            CrewAI Crew
            
        Raises:
            CrewAIError: If crew creation fails
        """
        try:
            # Create tasks
            relationship_task = create_relationship_analysis_task(
                self.data_explorer, entity_type, entity_id, entity_name
            )
            quality_task = create_data_quality_assessment_task(
                self.data_steward, entity_type, entity_id, entity_name
            )
            metadata_task = create_metadata_enhancement_task(
                self.metadata_expert, entity_type, entity_id, entity_name
            )
            
            # Create crew
            return Crew(
                agents=[self.data_explorer, self.data_steward, self.metadata_expert],
                tasks=[relationship_task, quality_task, metadata_task],
                process=Process.sequential,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Failed to create entity analysis crew: {e}")
            raise CrewAIError(f"Failed to create entity analysis crew: {e}")
    
    def rule_analysis_crew(self, rule_id: str, rule_name: str) -> Crew:
        """
        Create a crew for comprehensive rule analysis.
        
        Args:
            rule_id: ID of the rule
            rule_name: Name of the rule
            
        Returns:
            CrewAI Crew
            
        Raises:
            CrewAIError: If crew creation fails
        """
        try:
            # Create tasks
            rule_task = create_rule_analysis_task(
                self.business_analyst, rule_id, rule_name
            )
            data_scope_task = Task(
                description=f"""
                Analyze the data scope and impact of Rule '{rule_name}' (ID: {rule_id}).
                
                1. Identify all data elements and business objects affected by this rule.
                2. Map the rule's coverage across different domains.
                3. Assess whether the rule has appropriate scope or should be extended.
                4. Identify potential data quality issues if this rule is violated.
                5. Suggest monitoring approaches for this rule.
                
                Provide a comprehensive analysis of how this rule affects the data landscape.
                """,
                agent=self.data_explorer,
                context={"rule_id": rule_id, "rule_name": rule_name}
            )
            governance_task = Task(
                description=f"""
                Assess governance aspects of Rule '{rule_name}' (ID: {rule_id}).
                
                1. Analyze the rule's enforcement across systems.
                2. Evaluate the rule's documentation and clarity.
                3. Identify potential governance gaps or improvements.
                4. Suggest governance controls to ensure compliance.
                5. Provide recommendations for better rule management.
                
                Your assessment should help improve the governance of this rule.
                """,
                agent=self.data_steward,
                context={"rule_id": rule_id, "rule_name": rule_name}
            )
            
            # Create crew
            return Crew(
                agents=[self.business_analyst, self.data_explorer, self.data_steward],
                tasks=[rule_task, data_scope_task, governance_task],
                process=Process.sequential,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Failed to create rule analysis crew: {e}")
            raise CrewAIError(f"Failed to create rule analysis crew: {e}")


# Global crew instance
data_catalog_crew = DataCatalogCrew()


def run_similarity_search(query: str, entity_types: Optional[List[str]] = None) -> str:
    """
    Run a similarity search using CrewAI.
    
    Args:
        query: Search query text
        entity_types: Types of entities to search
        
    Returns:
        Analysis results as a string
        
    Raises:
        CrewAIError: If the operation fails
    """
    try:
        crew = data_catalog_crew.similarity_search_crew(query, entity_types)
        result = crew.kickoff()
        return result
    except Exception as e:
        logger.error(f"Similarity search operation failed: {e}")
        raise CrewAIError(f"Similarity search operation failed: {e}")


def run_entity_analysis(entity_type: str, entity_id: str, entity_name: str) -> str:
    """
    Run a comprehensive entity analysis using CrewAI.
    
    Args:
        entity_type: Type of entity to analyze
        entity_id: ID of the entity
        entity_name: Name of the entity
        
    Returns:
        Analysis results as a string
        
    Raises:
        CrewAIError: If the operation fails
    """
    try:
        crew = data_catalog_crew.entity_analysis_crew(entity_type, entity_id, entity_name)
        result = crew.kickoff()
        return result
    except Exception as e:
        logger.error(f"Entity analysis operation failed: {e}")
        raise CrewAIError(f"Entity analysis operation failed: {e}")


def run_rule_analysis(rule_id: str, rule_name: str) -> str:
    """
    Run a comprehensive rule analysis using CrewAI.
    
    Args:
        rule_id: ID of the rule
        rule_name: Name of the rule
        
    Returns:
        Analysis results as a string
        
    Raises:
        CrewAIError: If the operation fails
    """
    try:
        crew = data_catalog_crew.rule_analysis_crew(rule_id, rule_name)
        result = crew.kickoff()
        return result
    except Exception as e:
        logger.error(f"Rule analysis operation failed: {e}")
        raise CrewAIError(f"Rule analysis operation failed: {e}")