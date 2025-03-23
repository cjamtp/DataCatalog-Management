"""CrewAI agents for data catalog operations."""
from typing import Dict, List, Optional

from crewai import Agent
from loguru import logger

from src.config import settings
from src.utils.errors import CrewAIError


class AgentFactory:
    """Factory for creating CrewAI agents."""
    
    @staticmethod
    def create_data_explorer_agent() -> Agent:
        """
        Create a data explorer agent for discovering and analyzing data catalog entities.
        
        Returns:
            CrewAI Agent
            
        Raises:
            CrewAIError: If agent creation fails
        """
        try:
            return Agent(
                role="Data Explorer",
                goal="Discover and analyze relationships between business objects, data elements, domains, and rules",
                backstory="""You are an expert data explorer with deep knowledge of 
                data catalogs, business objects, data elements, and business rules. 
                You excel at finding connections between different data assets and 
                uncovering hidden patterns in the data landscape.""",
                verbose=True,
                allow_delegation=False,
                llm_model=settings.LLM_MODEL
            )
        except Exception as e:
            logger.error(f"Failed to create data explorer agent: {e}")
            raise CrewAIError(f"Failed to create data explorer agent: {e}")
    
    @staticmethod
    def create_business_analyst_agent() -> Agent:
        """
        Create a business analyst agent for interpreting business rules and contexts.
        
        Returns:
            CrewAI Agent
            
        Raises:
            CrewAIError: If agent creation fails
        """
        try:
            return Agent(
                role="Business Analyst",
                goal="Interpret business rules and provide business context for data assets",
                backstory="""You are a skilled business analyst who understands both 
                technical and business aspects of data. You excel at explaining 
                business rules, the rationale behind them, and their implications. 
                You can translate technical data concepts into business language.""",
                verbose=True,
                allow_delegation=True,
                llm_model=settings.LLM_MODEL
            )
        except Exception as e:
            logger.error(f"Failed to create business analyst agent: {e}")
            raise CrewAIError(f"Failed to create business analyst agent: {e}")
    
    @staticmethod
    def create_data_steward_agent() -> Agent:
        """
        Create a data steward agent for ensuring data quality and governance.
        
        Returns:
            CrewAI Agent
            
        Raises:
            CrewAIError: If agent creation fails
        """
        try:
            return Agent(
                role="Data Steward",
                goal="Ensure data quality and proper governance of data assets",
                backstory="""You are a meticulous data steward responsible for 
                maintaining data quality across the organization. You ensure that 
                data assets adhere to governance policies, have proper documentation, 
                and follow established standards. You identify potential quality 
                issues and suggest improvements.""",
                verbose=True,
                allow_delegation=True,
                llm_model=settings.LLM_MODEL
            )
        except Exception as e:
            logger.error(f"Failed to create data steward agent: {e}")
            raise CrewAIError(f"Failed to create data steward agent: {e}")
    
    @staticmethod
    def create_metadata_expert_agent() -> Agent:
        """
        Create a metadata expert agent for analyzing and enhancing metadata.
        
        Returns:
            CrewAI Agent
            
        Raises:
            CrewAIError: If agent creation fails
        """
        try:
            return Agent(
                role="Metadata Expert",
                goal="Analyze and enhance metadata for data catalog entities",
                backstory="""You are a metadata specialist with expertise in 
                organizing and structuring information about data assets. You excel 
                at creating meaningful descriptions, classifications, and tags for 
                data elements and business objects. You understand how metadata 
                enhances discoverability and usability of data.""",
                verbose=True,
                allow_delegation=True,
                llm_model=settings.LLM_MODEL
            )
        except Exception as e:
            logger.error(f"Failed to create metadata expert agent: {e}")
            raise CrewAIError(f"Failed to create metadata expert agent: {e}")


# Easy access functions for agents
def get_data_explorer_agent() -> Agent:
    """Get a data explorer agent."""
    return AgentFactory.create_data_explorer_agent()

def get_business_analyst_agent() -> Agent:
    """Get a business analyst agent."""
    return AgentFactory.create_business_analyst_agent()

def get_data_steward_agent() -> Agent:
    """Get a data steward agent."""
    return AgentFactory.create_data_steward_agent()

def get_metadata_expert_agent() -> Agent:
    """Get a metadata expert agent."""
    return AgentFactory.create_metadata_expert_agent()