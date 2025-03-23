#!/usr/bin/env python
"""
Database initialization script for the data catalog application.

This script initializes the Neo4j database with constraints and indexes for
business objects, data elements, domains, and rules.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from loguru import logger

from src.db.neo4j_client import neo4j_client
from src.utils.errors import DatabaseError


def init_database():
    """Initialize the Neo4j database with constraints and indexes."""
    try:
        # Initialize constraints
        logger.info("Initializing database constraints...")
        neo4j_client.init_constraints()
        
        # Initialize indexes
        logger.info("Initializing database indexes...")
        neo4j_client.init_indexes()
        
        logger.success("Database initialization completed successfully")
        return True
    except DatabaseError as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False
    finally:
        # Close connection
        neo4j_client.close()


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    success = init_database()
    sys.exit(0 if success else 1)