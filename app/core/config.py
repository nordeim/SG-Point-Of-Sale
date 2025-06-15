# File: app/core/config.py
"""
Manages all application configuration.

This module uses Pydantic's BaseSettings to provide a strongly-typed configuration
model that loads settings from environment variables and a .env file. This ensures
that all configuration is validated at startup.
"""
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """
    Application settings model.
    Pydantic automatically reads values from environment variables or a .env file.
    The names are case-insensitive.
    """
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    APP_ENV: str = Field("production", env="APP_ENV")
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        # Specifies the env file to load for local development.
        # Ensure you have a .env.dev file based on .env.example
        env_file = ".env.dev"
        env_file_encoding = "utf-8"

# Create a single, importable instance of the settings.
# The application will import this `settings` object to access configuration.
settings = Settings()
