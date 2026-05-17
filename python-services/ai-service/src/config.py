# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Configuration settings for the AI Service.

Loaded from environment variables or a .env file at startup.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All runtime configuration for the ai-service.

    Fields are populated from environment variables (case-insensitive).
    Defaults allow the service to start locally without any extra setup,
    though ``openai_api_key`` must be set for analysis calls to succeed.
    """

    service_name: str = "ai-service"
    service_port: int = 8003

    openai_api_key: str = ""
    # Optional: set to a custom base URL to use OpenAI-compatible providers
    # e.g. https://api.groq.com/openai/v1 for Groq (free tier)
    openai_base_url: str = ""
    openai_model: str = "llama-3.3-70b-versatile"
    openai_max_tokens: int = 2000

    content_service_url: str = "http://localhost:8002"
    auth_service_url: str = "http://localhost:8081"

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic settings configuration."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
