"""Configuration for AI Service"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Service configuration
    service_name: str = "ai-service"
    service_port: int = 8003
    
    # OpenAI configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
