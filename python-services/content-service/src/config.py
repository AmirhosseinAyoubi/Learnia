from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "content-service"
    service_port: int = 8002
    database_url: str = "postgresql://learnia_user:learnia_pass@localhost:5432/learnia_content_db"
    auth_service_url: str = "http://localhost:8081"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
