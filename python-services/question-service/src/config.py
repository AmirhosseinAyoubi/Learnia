"""Configuration for Question Service"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Service configuration
    service_name: str = "question-service"
    service_port: int = 8004
    
    # Database configuration
    database_url: str = "postgresql://learnia_user:learnia_pass@localhost:5432/learnia_question_db"
    
    # Service URLs
    content_service_url: str = "http://localhost:8002"
    ai_service_url: str = "http://localhost:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
