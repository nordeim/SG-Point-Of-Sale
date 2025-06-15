# File: app/core/config.py
"""
Manages all application configuration.

This module uses Pydantic's BaseSettings to provide a strongly-typed configuration
model that loads settings from environment variables and a .env file. This ensures
that all configuration is validated at startup.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict # Use pydantic_settings for newer Pydantic versions

class Settings(BaseSettings):
    """
    Application settings model.
    Pydantic automatically reads values from environment variables or a .env file.
    The names are case-insensitive.
    """
    model_config = SettingsConfigDict(
        env_file='.env.dev', # Specifies the env file to load for local development.
        env_file_encoding='utf-8',
        extra='ignore' # Allow extra environment variables not defined in the model
    )

    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database connection URL")

    # Application-level settings
    APP_ENV: str = Field("development", description="Application environment (e.g., 'development', 'production')")
    DEBUG: bool = Field(True, description="Enable debug mode (e.g., SQLAlchemy echoing)")
    LOG_LEVEL: str = Field("DEBUG", description="Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')")
    SECRET_KEY: str = Field(..., description="Secret key for security purposes (e.g., session management, hashing)")

    # Context IDs for current company/outlet/user (for development/testing convenience)
    # In production, these would be derived from authentication/session.
    CURRENT_COMPANY_ID: str = Field("00000000-0000-0000-0000-000000000001", description="Placeholder for current company UUID")
    CURRENT_OUTLET_ID: str = Field("00000000-0000-0000-0000-000000000002", description="Placeholder for current outlet UUID")
    CURRENT_USER_ID: str = Field("00000000-0000-0000-0000-000000000003", description="Placeholder for current user UUID")

# Create a single, importable instance of the settings.
# The application will import this `settings` object to access configuration.
settings = Settings()
