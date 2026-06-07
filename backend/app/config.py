import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Gateway Configs
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database URL
    DATABASE_URL: str = "sqlite:///./travelmind.db"

    # LLM Settings
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # SerpAPI for Hotel Search
    SERPAPI_API_KEY: str

    # Vector DB
    CHROMA_DB_PATH: str = "./chroma_db"

    # LangSmith Tracing (Optional)
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "travelmind-ai"

    # Force reading from environment or .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings singleton
settings = Settings()
