from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    DATABASE_URL: str = "sqlite:///./data/analytics.db"
    MODEL_NAME: str = "mistral-tiny"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 