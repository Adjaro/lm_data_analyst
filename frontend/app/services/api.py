import requests
from typing import Dict, Any, List, Optional
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from datetime import datetime, timedelta
import json
from functools import lru_cache

logger = logging.getLogger(__name__)

class APIService:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000/api")
        self.session = self._create_session()
        self.last_health_check = None
        self.health_check_interval = 60  # secondes

    def _create_session(self) -> requests.Session:
        """Crée une session avec retry automatique."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _check_health(self) -> bool:
        """Vérifie la santé du backend avec cache."""
        current_time = datetime.now()
        
        # Utilise le cache si la dernière vérification est récente
        if (self.last_health_check and 
            (current_time - self.last_health_check).total_seconds() < self.health_check_interval):
            return True

        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            self.last_health_check = current_time
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def analyze_query(
        self,
        prompt: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Analyse une requête avec pagination."""
        if not self._check_health():
            raise ConnectionError("Le service backend n'est pas disponible")

        try:
            response = self.session.post(
                f"{self.base_url}/query",
                json={
                    "prompt": prompt,
                    "page": page,
                    "page_size": page_size
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError("La requête a expiré. Veuillez réessayer.")
            
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                error_detail = e.response.json().get('detail', str(e))
                raise ConnectionError(f"Erreur de connexion: {error_detail}")
            raise ConnectionError(f"Erreur de connexion: {str(e)}")
            
        except Exception as e:
            raise Exception(f"Erreur inattendue: {str(e)}")

    def get_health_status(self) -> Dict[str, Any]:
        """Récupère le statut détaillé du backend."""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                "status": "unhealthy",
                "version": "unknown",
                "database_status": "unknown",
                "ai_service_status": "unknown"
            } 