"""
Application Configuration Settings

This module defines the configuration settings for the Product Management API
using Pydantic Settings for environment-based configuration management.

The configuration supports:
- Application metadata (name, debug mode)
- Database connection settings
- Environment variable overrides
- Development and production configurations

Author: Product Management Team
Version: 1.0.0
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings configuration class.

    This class defines all configurable settings for the application
    using Pydantic Settings for type validation and environment variable
    support. Settings can be overridden via environment variables or
    a .env file.

    Attributes:
        app_name (str): Name of the FastAPI application, defaults to "FastAPI Template"
        database_url (str): SQLAlchemy database URL, defaults to SQLite with async support
        debug (bool): Enable debug mode for development, defaults to True

    Environment Variables:
        All attributes can be overridden using environment variables with
        the same name in uppercase (e.g., APP_NAME, DATABASE_URL, DEBUG).

    Configuration:
        - Reads from .env file if present
        - Environment variables take precedence over defaults
        - Type validation ensures correct data types

    Examples:
        # Using defaults
        settings = Settings()

        # Override with environment variables
        export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db"
        export DEBUG=false
        settings = Settings()
    """
    app_name: str = "FastAPI Template"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    debug: bool = True

    class Config:
        """
        Pydantic configuration for Settings class.

        This inner class configures how Pydantic handles the settings:
        - env_file: Specifies the .env file to read configuration from
        """
        env_file = ".env"


# Global settings instance used throughout the application
settings = Settings()
