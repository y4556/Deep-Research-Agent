from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Find the .env file in the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # 🆓 FREE API Keys (REQUIRED - No rate limits!)
    GROQ_API_KEY: str        # Get free from https://console.groq.com
    OPENROUTER_API_KEY: str  # Get free from https://openrouter.ai
    TAVILY_API_KEY: str      # Get free from https://tavily.com (free tier: 1000 requests/month)
    
    # 💰 Optional API Keys (Leave empty if not using)
    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    
    # Google Custom Search (Fallback for Tavily)
    GOOGLE_CUSTOM_SEARCH_API_KEY: str = ""  # Get from https://console.cloud.google.com
    GOOGLE_CSE_ID: str = "46f410e1fc8c44c23"  # Deep Research Agent Custom Search Engine ID
    
    # LangSmith (Optional - for monitoring)
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "deep-research-agent"
    LANGCHAIN_TRACING_V2: bool = False  # Disabled by default
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
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields in .env file
        case_sensitive = False  # Allow case-insensitive field names

settings = Settings()