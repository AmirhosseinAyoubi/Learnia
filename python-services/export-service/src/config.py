# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Configuration settings for the Export Service.

Loaded from environment variables or a .env file at startup.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All runtime configuration for the export-service.

    Fields are populated from environment variables (case-insensitive).
    Defaults target the Rahti deployment URLs so the service works
    out-of-the-box in production without additional configuration.
    """

    service_name: str = "export-service"
    service_port: int = 8004

    ai_service_url: str = "http://ai-service:8003"
    auth_service_url: str = "http://auth-service:8081"

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic settings configuration."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
