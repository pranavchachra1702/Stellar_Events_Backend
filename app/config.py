"""
Configuration module for Evently backend.

This file defines application settings using Pydantic's `BaseSettings`.
Environment variables are automatically loaded from `.env`.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL (str): Connection string for the PostgreSQL database.
        INIT_DB (bool): Flag to determine whether to initialize DB schema on startup.
    """
    DATABASE_URL: str
    INIT_DB: bool = False

    class Config:
        """Configuration to specify environment file for local development."""
        env_file = ".env"


# Global settings instance accessible across modules
settings = Settings()
