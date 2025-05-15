import requests
from typing import Dict, Any, List
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)

class APIService:
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000/api")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
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
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def analyze_query(self, prompt: str) -> Dict[str, Any]:
        if not self._check_health():
            raise ConnectionError("Le service backend n'est pas disponible")

        try:
            response = self.session.post(
                f"{self.base_url}/query",
                json={"prompt": prompt},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TimeoutError("La requête a expiré. Veuillez réessayer.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erreur de connexion: {str(e)}")
        except Exception as e:
            raise Exception(f"Erreur inattendue: {str(e)}") 