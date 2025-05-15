import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from backend.app.core.config import settings

class SecretFilter(logging.Filter):
    """Filtre pour masquer les secrets dans les logs."""
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = record.msg.replace(settings.SECRET_KEY, "***SECRET_KEY***")
            record.msg = record.msg.replace(settings.MISTRAL_API_KEY, "***MISTRAL_API_KEY***")
        return True

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
    console_handler.addFilter(SecretFilter())
    
    # Handler pour les fichiers
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.addFilter(SecretFilter())
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    # Évite la duplication de handlers
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
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
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(console_handler)
        if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
            logger.addHandler(file_handler)
        logger.addFilter(SecretFilter())

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 