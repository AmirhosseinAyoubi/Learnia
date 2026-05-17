# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Configuration settings for the Processing Service.

Loaded from environment variables or a .env file at startup.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All runtime configuration for the processing-service.

    Fields are populated from environment variables (case-insensitive).
    Defaults allow the service to start locally without any extra setup.
    """

    service_name: str = "processing-service"
    service_port: int = 8001

    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "document.processing"

    document_service_url: str = "http://localhost:8084"
    content_service_url: str = "http://localhost:8002"
    ai_service_url: str = "http://localhost:8003"

    internal_api_key: str = ""

    max_file_size: int = 100 * 1024 * 1024  # 100 MB

    # Base directory where uploaded files are stored on disk.
    # The document-service mounts the PVC at /app/uploads; paths in older
    # records may be stored as /uploads/... (without the /app prefix).
    file_upload_dir: str = "/app/uploads"

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic settings configuration."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
