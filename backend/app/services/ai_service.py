from transformers import pipeline
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

class AIService:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model=settings.CLASSIFIER_MODEL
        )
        self.mistral_client = MistralClient(api_key=settings.MISTRAL_API_KEY)
        logger.info("AI Service initialized")

    def generate_sql_query(self, prompt: str) -> str:
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="You are a SQL expert. Generate a SQL query based on the user's request."
                ),
                ChatMessage(
                    role="user",
                    content=f"Generate a SQL query for: {prompt}"
                )
            ]
            
            response = self.mistral_client.chat(
                model=settings.MODEL_NAME,
                messages=messages
            )
            
            sql_query = response.choices[0].message.content
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise

    def determine_visualization_type(self, prompt: str) -> str:
        try:
            result = self.classifier(prompt)
            logger.info(f"Classification result: {result}")
            
            prompt_lower = prompt.lower()
            if "trend" in prompt_lower or "evolution" in prompt_lower:
                return "line"
            elif "distribution" in prompt_lower or "frequency" in prompt_lower:
                return "histogram"
            elif "proportion" in prompt_lower or "percentage" in prompt_lower:
                return "pie"
            else:
                return "bar"
                
        except Exception as e:
            logger.error(f"Error determining visualization type: {str(e)}")
            return "bar"  # Type par défaut en cas d'erreur 