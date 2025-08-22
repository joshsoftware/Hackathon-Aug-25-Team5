# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Database - directly from environment
    DATABASE_URL: str = os.getenv("DATABASE_URL", "") 
    # AI API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Crawling
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "AI-Service-Bot/1.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
