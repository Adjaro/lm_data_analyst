from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Informations de base
    PROJECT_NAME: str = "Data Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Sécurité
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./data/analytics.db"
    
    # API Keys
    MISTRAL_API_KEY: str
    
    # Configuration du modèle
    MODEL_NAME: str = "distilbert-base-uncased"
    MODEL_CACHE_DIR: str = "./model_cache"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Retourne les paramètres de configuration en cache."""
    return Settings()

settings = get_settings() 