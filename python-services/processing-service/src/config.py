"""Configuration for Processing Service"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Service configuration
    service_name: str = "processing-service"
    service_port: int = 8001
    
    # RabbitMQ configuration
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "document_processing"
    
    # Document Service URL
    document_service_url: str = "http://localhost:8084"
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
