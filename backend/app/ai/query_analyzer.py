from transformers import pipeline
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from ..config import settings

class QueryAnalyzer:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="distilbert-base-uncased")
        self.mistral_client = MistralClient(api_key=settings.MISTRAL_API_KEY)

    def generate_sql_query(self, prompt: str) -> str:
        messages = [
            ChatMessage(role="system", content="You are a SQL expert. Generate a SQL query based on the user's request."),
            ChatMessage(role="user", content=f"Generate a SQL query for: {prompt}")
        ]
        
        response = self.mistral_client.chat(
            model=settings.MODEL_NAME,
            messages=messages
        )
        
        return response.choices[0].message.content

    def determine_visualization_type(self, prompt: str) -> str:
        result = self.classifier(prompt)
        
        if "trend" in prompt.lower() or "evolution" in prompt.lower():
            return "line"
        elif "distribution" in prompt.lower() or "frequency" in prompt.lower():
            return "histogram"
        elif "proportion" in prompt.lower() or "percentage" in prompt.lower():
            return "pie"
        else:
            return "bar" 