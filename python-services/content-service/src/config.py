"""Configuration for Content Service"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Service configuration
    service_name: str = "content-service"
    service_port: int = 8002
    
    # Database configuration
    database_url: str = "postgresql://learnia_user:learnia_pass@localhost:5432/learnia_content_db"
    
    # OpenAI configuration
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    
    # AI Service URL
    ai_service_url: str = "http://localhost:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
