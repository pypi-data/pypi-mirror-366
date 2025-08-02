"""
FastAPI application factory for Authly.

This module provides a centralized way to create and configure FastAPI applications
for different deployment scenarios (production, development, embedded).
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from authly.api import auth_router, health_router, oauth_router, oidc_router, users_router
from authly.api.admin_middleware import setup_admin_middleware
from authly.api.admin_router import admin_router
from authly.api.oauth_discovery_router import oauth_discovery_router
from authly.api.password_change import router as password_change_router
from authly.config import AuthlyConfig


def create_app(
    config: Optional[AuthlyConfig] = None,
    title: str = "Authly Authentication Service",
    version: str = "0.1.5",
    description: str = "Production-ready authentication and authorization service",
    lifespan: Optional[AsyncGenerator] = None,
    static_path: Optional[str] = None,
    api_prefix: Optional[str] = None,
) -> FastAPI:
    """
    Create and configure a FastAPI application for Authly.

    Args:
        config: AuthlyConfig instance (optional, will use defaults if not provided)
        title: Application title
        version: Application version
        description: Application description
        lifespan: Lifespan context manager (optional)
        static_path: Path to static files directory (optional)
        api_prefix: API prefix for versioned routes (optional)

    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(title=title, version=version, description=description, lifespan=lifespan)

    # Setup admin security middleware
    setup_admin_middleware(app)

    # Mount static files for OAuth templates
    if static_path is None:
        static_path = os.path.join(os.path.dirname(__file__), "static")

    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")

    # Include health router (no prefix)
    app.include_router(health_router)

    # Get API prefix from config, parameter, or environment
    if api_prefix is None:
        if config:
            api_prefix = config.fastapi_api_version_prefix
        else:
            api_prefix = os.getenv("AUTHLY_API_PREFIX", "/api/v1")

    # Include versioned API routers
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(password_change_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(oauth_router, prefix=api_prefix)

    # Include OIDC router (no prefix - uses well-known paths)
    app.include_router(oidc_router)

    # Include OAuth discovery router (no prefix - RFC 8414 compliance)
    app.include_router(oauth_discovery_router)

    # Include admin router (no prefix - has its own /admin prefix)
    app.include_router(admin_router)

    # Configure OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=title,
            version=version,
            description=description,
            routes=app.routes,
        )

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app


def create_production_app(lifespan: AsyncGenerator) -> FastAPI:
    """
    Create a production-ready FastAPI application.

    Args:
        lifespan: Lifespan context manager for resource management

    Returns:
        Configured FastAPI application for production use
    """
    return create_app(
        title="Authly Authentication Service",
        version="0.1.5",
        description="Production-ready authentication and authorization service with OAuth 2.1 support",
        lifespan=lifespan,
    )


def create_embedded_app(config: AuthlyConfig, database_url: str, seed: bool = False) -> FastAPI:
    """
    Create a FastAPI application for embedded development mode.

    Args:
        config: AuthlyConfig instance
        database_url: Database connection URL
        seed: Whether to seed test data

    Returns:
        Configured FastAPI application for embedded development
    """
    app = create_app(
        config=config,
        title="Authly Auth API (Embedded)",
        version="0.1.5",
        description="Authly Authentication and Authorization Service - Embedded Development Mode",
        api_prefix=config.fastapi_api_version_prefix,
    )

    # Configuration will be available through resource manager dependency injection
    # No direct app.state storage needed - use get_resource_manager() dependency

    return app
