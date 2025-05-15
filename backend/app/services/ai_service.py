from transformers import pipeline
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from ..core.config import settings
from ..core.logging import get_logger
import re
from functools import lru_cache
from typing import Optional, Dict, Any
import sqlparse
from sqlparse.sql import Token, TokenType

logger = get_logger(__name__)

class AIService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_models()
            self._initialized = True
            logger.info("AI Service initialized")

    def _load_models(self):
        """Charge les modèles une seule fois."""
        try:
            self.classifier = pipeline(
                "text-classification",
                model=settings.CLASSIFIER_MODEL,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            self.mistral_client = MistralClient(api_key=settings.MISTRAL_API_KEY)
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise RuntimeError("Failed to initialize AI models")

    def _validate_sql_query(self, query: str) -> bool:
        """Valide que la requête SQL est sécurisée."""
        try:
            # Parse la requête SQL
            parsed = sqlparse.parse(query)[0]
            
            # Vérifie que c'est une requête SELECT
            if not parsed.get_type().upper() == 'SELECT':
                logger.warning("Query is not a SELECT statement")
                return False
            
            # Liste des tokens autorisés
            allowed_tokens = {
                TokenType.Keyword: {'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'IS', 'NULL', 'ASC', 'DESC'},
                TokenType.Whitespace: None,  # Tous les espaces sont autorisés
                TokenType.Identifier: None,  # Tous les identifiants sont autorisés
                TokenType.Number: None,      # Tous les nombres sont autorisés
                TokenType.String: None,      # Toutes les chaînes sont autorisées
                TokenType.Operator: {'=', '>', '<', '>=', '<=', '<>', '!=', '+', '-', '*', '/'},
                TokenType.Punctuation: {',', '.', '(', ')', ';'},
            }
            
            # Vérifie chaque token
            for token in parsed.tokens:
                if token.ttype in allowed_tokens:
                    if allowed_tokens[token.ttype] is not None:
                        if token.value.upper() not in allowed_tokens[token.ttype]:
                            logger.warning(f"Unauthorized token: {token.value}")
                            return False
                else:
                    logger.warning(f"Unauthorized token type: {token.ttype}")
                    return False
            
            # Vérifie la profondeur des sous-requêtes
            subquery_depth = 0
            for token in parsed.tokens:
                if token.ttype == TokenType.Punctuation and token.value == '(':
                    subquery_depth += 1
                elif token.ttype == TokenType.Punctuation and token.value == ')':
                    subquery_depth -= 1
                if subquery_depth > 3:  # Limite la profondeur des sous-requêtes
                    logger.warning("Query has too many nested subqueries")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating SQL query: {str(e)}")
            return False

    def _sanitize_prompt(self, prompt: str) -> str:
        """Nettoie et valide le prompt."""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
            
        # Supprime les caractères spéciaux dangereux
        sanitized = re.sub(r'[;\\\'"`]', '', prompt)
        
        # Vérifie la longueur
        if len(sanitized) > 500:
            raise ValueError("Prompt is too long (max 500 characters)")
            
        # Vérifie le contenu
        if re.search(r'\b(exec|execute|sp_|xp_|sysobjects|syscolumns)\b', sanitized, re.I):
            raise ValueError("Prompt contains potentially dangerous SQL keywords")
            
        return sanitized

    def generate_sql_query(self, prompt: str) -> str:
        """Génère une requête SQL sécurisée à partir du prompt."""
        try:
            # Nettoie le prompt
            sanitized_prompt = self._sanitize_prompt(prompt)
            
            messages = [
                ChatMessage(
                    role="system",
                    content="""You are a SQL expert. Generate a SQL query based on the user's request.
                    Rules:
                    1. Only generate SELECT queries
                    2. Do not include any DML or DDL operations
                    3. Use proper table aliases
                    4. Include comments explaining the query
                    5. Use parameterized queries where possible
                    6. Avoid dynamic SQL
                    7. Use proper SQL injection prevention techniques"""
                ),
                ChatMessage(
                    role="user",
                    content=f"Generate a SQL query for: {sanitized_prompt}"
                )
            ]
            
            response = self.mistral_client.chat(
                model=settings.MODEL_NAME,
                messages=messages
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Valide la requête générée
            if not self._validate_sql_query(sql_query):
                logger.warning(f"Generated unsafe SQL query: {sql_query}")
                raise ValueError("Generated SQL query is not safe")
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise RuntimeError("Failed to generate SQL query") from e

    def determine_visualization_type(self, prompt: str) -> str:
        """Détermine le type de visualisation approprié."""
        try:
            # Nettoie le prompt
            sanitized_prompt = self._sanitize_prompt(prompt)
            
            # Utilise le cache si disponible
            cached_result = self.get_cached_classification(sanitized_prompt)
            if cached_result and cached_result.get("type"):
                return cached_result["type"]
            
            # Classification du prompt
            result = self.classifier(sanitized_prompt)
            logger.info(f"Classification result: {result}")
            
            # Analyse sémantique du prompt
            prompt_lower = sanitized_prompt.lower()
            
            # Règles de décision pour le type de visualisation
            if any(word in prompt_lower for word in ["trend", "evolution", "time", "period"]):
                return "line"
            elif any(word in prompt_lower for word in ["distribution", "frequency", "histogram"]):
                return "histogram"
            elif any(word in prompt_lower for word in ["proportion", "percentage", "ratio", "part"]):
                return "pie"
            elif any(word in prompt_lower for word in ["compare", "comparison", "versus"]):
                return "bar"
            else:
                return "bar"  # Type par défaut
                
        except Exception as e:
            logger.error(f"Error determining visualization type: {str(e)}")
            return "bar"  # Type par défaut en cas d'erreur

    @staticmethod
    @lru_cache(maxsize=100)
    def get_cached_classification(prompt: str) -> Dict[str, Any]:
        """Cache les résultats de classification pour les prompts identiques."""
        return {"type": "bar"}  # Valeur par défaut 