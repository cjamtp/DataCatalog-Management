"""Configuration settings for the data catalog application."""
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    NEO4J_URI: str = Field(..., description="Neo4j database URI")
    NEO4J_USERNAME: str = Field(..., description="Neo4j database username")
    NEO4J_PASSWORD: str = Field(..., description="Neo4j database password")
    NEO4J_DATABASE: str = Field("neo4j", description="Neo4j database name")
    
    # API settings
    API_HOST: str = Field("0.0.0.0", description="API host address")
    API_PORT: int = Field(8000, description="API port")
    API_PREFIX: str = Field("/api/v1", description="API route prefix")
    
    # CrewAI settings
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    LLM_MODEL: str = Field("gpt-4", description="LLM model for CrewAI agents")
    
    # Embedding settings
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", description="Sentence embedding model")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        description="Log format"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
