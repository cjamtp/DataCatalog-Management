"""FastAPI application for data catalog management."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.routes import business_objects, data_elements, domains, rules, search
from src.config import settings
from src.utils.errors import CatalogError


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Data Catalog API",
        description="API for managing business objects, data elements, domains, and rules",
        version="0.1.0",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handler for custom errors
    @app.exception_handler(CatalogError)
    async def catalog_error_handler(request: Request, exc: CatalogError):
        """Handle custom catalog errors."""
        logger.error(f"CatalogError: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={"error": exc.message},
        )
    
    # Include routers
    app.include_router(
        business_objects.router,
        prefix=f"{settings.API_PREFIX}/business-objects",
        tags=["Business Objects"],
    )
    app.include_router(
        data_elements.router,
        prefix=f"{settings.API_PREFIX}/data-elements",
        tags=["Data Elements"],
    )
    app.include_router(
        domains.router,
        prefix=f"{settings.API_PREFIX}/domains",
        tags=["Domains"],
    )
    app.include_router(
        rules.router,
        prefix=f"{settings.API_PREFIX}/rules",
        tags=["Rules"],
    )
    app.include_router(
        search.router,
        prefix=f"{settings.API_PREFIX}/search",
        tags=["Search"],
    )
    
    @app.get("/", tags=["Health"])
    async def health_check():
        """API health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}
    
    return app


app = create_app()