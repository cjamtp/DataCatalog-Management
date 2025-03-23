"""
Entry point for the data catalog management system.

This script initializes and runs the FastAPI application.
"""
import uvicorn
from loguru import logger

from src.api.app import app
from src.config import settings
from src.utils.logging import configure_logging


def run_api():
    """
    Run the FastAPI application with configured settings.
    """
    logger.info(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    # Configure logging
    configure_logging()
    
    # Run API server
    run_api()