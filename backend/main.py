from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sqlite3
from transformers import pipeline
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuration des clients
classifier = pipeline("text-classification", model="distilbert-base-uncased")
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    data: List[Dict[str, Any]]
    visualization_type: str
    title: str

def get_db_connection():
    return sqlite3.connect('data/analytics.db')

def generate_sql_query(prompt: str) -> str:
    # Utiliser Mistral pour générer la requête SQL
    messages = [
        ChatMessage(role="system", content="You are a SQL expert. Generate a SQL query based on the user's request."),
        ChatMessage(role="user", content=f"Generate a SQL query for: {prompt}")
    ]
    
    response = mistral_client.chat(
        model="mistral-tiny",
        messages=messages
    )
    
    return response.choices[0].message.content

def determine_visualization_type(prompt: str) -> str:
    # Utiliser le classificateur pour déterminer le type de visualisation
    result = classifier(prompt)
    # Logique simple pour déterminer le type de graphique
    if "trend" in prompt.lower() or "evolution" in prompt.lower():
        return "line"
    elif "distribution" in prompt.lower() or "frequency" in prompt.lower():
        return "histogram"
    elif "proportion" in prompt.lower() or "percentage" in prompt.lower():
        return "pie"
    else:
        return "bar"

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Générer la requête SQL
        sql_query = generate_sql_query(request.prompt)
        
        # Exécuter la requête
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = [dict(zip([col[0] for col in cursor.description], row)) 
                for row in cursor.fetchall()]
        conn.close()
        
        # Déterminer le type de visualisation
        viz_type = determine_visualization_type(request.prompt)
        
        return QueryResponse(
            data=data,
            visualization_type=viz_type,
            title=request.prompt
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 