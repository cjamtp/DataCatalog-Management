"""Logging configuration for the data catalog application."""
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.config import settings


def configure_logging(log_file: Optional[Path] = None) -> None:
    """
    Configure application logging.
    
    Args:
        log_file: Optional path to log file
    """
    # Remove default handler
    logger.remove()
    
    # Configure log format
    log_format = settings.LOG_FORMAT
    
    # Add console handler
    logger.add(
        sys.stderr, 
        level=settings.LOG_LEVEL,
        format=log_format,
        colorize=True
    )
    
    # Add file handler if specified
    if log_file or settings.LOG_FILE:
        file_path = log_file or settings.LOG_FILE
        logger.add(
            file_path,
            level=settings.LOG_LEVEL,
            format=log_format,
            rotation="10 MB",  # Rotate when file reaches 10 MB
            retention="1 week",  # Keep logs for 1 week
            compression="zip"  # Compress rotated logs
        )
    
    logger.info(f"Logging configured with level {settings.LOG_LEVEL}")


# Initialize logging when module is imported
configure_logging()