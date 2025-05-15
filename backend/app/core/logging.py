import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import settings

def setup_logging() -> None:
    """Configure le système de logging."""
    # Création du dossier de logs si nécessaire
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du format de log
    log_format = logging.Formatter(settings.LOG_FORMAT)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # Handler pour les fichiers
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configuration des loggers spécifiques
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy",
        "transformers"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(settings.LOG_LEVEL)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 