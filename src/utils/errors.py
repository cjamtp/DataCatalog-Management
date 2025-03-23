"""Custom error classes for the data catalog application."""


class CatalogError(Exception):
    """Base class for all catalog application errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseError(CatalogError):
    """Error related to database operations."""
    pass


class RepositoryError(CatalogError):
    """Error related to repository operations."""
    pass


class NotFoundError(CatalogError):
    """Error when an entity is not found."""
    pass


class ValidationError(CatalogError):
    """Error when input validation fails."""
    pass


class EmbeddingError(CatalogError):
    """Error related to embedding operations."""
    pass


class SearchError(CatalogError):
    """Error related to search operations."""
    pass


class APIError(CatalogError):
    """Error related to API operations."""
    pass


class ConfigError(CatalogError):
    """Error related to configuration."""
    pass


class CrewAIError(CatalogError):
    """Error related to CrewAI operations."""
    pass