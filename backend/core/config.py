from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    SERPER_API_KEY: str
    
    # LangSmith
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str = "deep-research-agent"
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # Application
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:8501"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # Research Configuration
    MAX_RESEARCH_DEPTH: int = 3
    DEFAULT_SEARCH_RESULTS: int = 5
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()