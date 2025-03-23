"""Neo4j database client for the data catalog application."""
from typing import Any, Dict, List, Optional

from loguru import logger
from neo4j import GraphDatabase, Session, exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.errors import DatabaseError


class Neo4jClient:
    """Client for Neo4j database operations."""
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Neo4jClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Neo4j connection if not already initialized."""
        if self._initialized:
            return
            
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session(database=settings.NEO4J_DATABASE) as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j database")
            self._initialized = True
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    def close(self):
        """Close the Neo4j connection."""
        if hasattr(self, "driver"):
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        
        Args:
            query: Cypher query to execute
            params: Query parameters
            
        Returns:
            List of records as dictionaries
            
        Raises:
            DatabaseError: If query execution fails
        """
        if params is None:
            params = {}
            
        try:
            with self.driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run(query, params)
                return [dict(record) for record in result]
        except exceptions.Neo4jError as e:
            logger.error(f"Neo4j query failed: {e}")
            logger.debug(f"Query: {query}, Params: {params}")
            raise DatabaseError(f"Database query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    def get_session(self) -> Session:
        """
        Get a Neo4j session for transaction management.
        
        Returns:
            Neo4j session
        """
        return self.driver.session(database=settings.NEO4J_DATABASE)
    
    def init_constraints(self):
        """Initialize database constraints for data catalog entities."""
        constraints = [
            """CREATE CONSTRAINT unique_business_object IF NOT EXISTS 
               FOR (o:BusinessObject) REQUIRE o.object_id IS UNIQUE""",
            
            """CREATE CONSTRAINT unique_data_element IF NOT EXISTS 
               FOR (e:DataElement) REQUIRE e.element_id IS UNIQUE""",
            
            """CREATE CONSTRAINT unique_rule IF NOT EXISTS 
               FOR (r:Rule) REQUIRE r.rule_id IS UNIQUE""",
            
            """CREATE CONSTRAINT unique_domain IF NOT EXISTS 
               FOR (d:Domain) REQUIRE d.domain_id IS UNIQUE"""
        ]
        
        for constraint in constraints:
            try:
                self.execute_query(constraint)
            except DatabaseError as e:
                logger.error(f"Failed to create constraint: {e}")
                raise
        
        logger.info("Database constraints initialized successfully")
    
    def init_indexes(self):
        """Initialize database indexes for data catalog entities."""
        indexes = [
            """CREATE INDEX business_object_name IF NOT EXISTS 
               FOR (o:BusinessObject) ON (o.name)""",
            
            """CREATE INDEX data_element_name IF NOT EXISTS 
               FOR (e:DataElement) ON (e.name)""",
            
            """CREATE INDEX rule_name IF NOT EXISTS 
               FOR (r:Rule) ON (r.name)""",
            
            """CREATE INDEX domain_name IF NOT EXISTS 
               FOR (d:Domain) ON (d.name)""",
               
            """CREATE INDEX embedding_index IF NOT EXISTS 
               FOR (n) ON (n.embedding)"""
        ]
        
        for index in indexes:
            try:
                self.execute_query(index)
            except DatabaseError as e:
                logger.error(f"Failed to create index: {e}")
                raise
        
        logger.info("Database indexes initialized successfully")


# Global client instance
neo4j_client = Neo4jClient()