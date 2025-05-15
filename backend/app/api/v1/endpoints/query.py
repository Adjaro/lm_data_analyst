from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ....db.base import get_db
from ....services.ai_service import AIService
from ....core.logging import get_logger
from pydantic import BaseModel

router = APIRouter()
logger = get_logger(__name__)
ai_service = AIService()

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    data: List[Dict[str, Any]]
    visualization_type: str
    title: str
    sql_query: str

class HealthResponse(BaseModel):
    status: str
    version: str
    database_status: str

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database_status=db_status
    )

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing query: {request.prompt}")
        
        # Générer la requête SQL
        sql_query = ai_service.generate_sql_query(request.prompt)
        
        # Exécuter la requête
        result = db.execute(sql_query)
        data = [dict(zip([col[0] for col in result.cursor.description], row)) 
                for row in result.fetchall()]
        
        # Déterminer le type de visualisation
        viz_type = ai_service.determine_visualization_type(request.prompt)
        
        return QueryResponse(
            data=data,
            visualization_type=viz_type,
            title=request.prompt,
            sql_query=sql_query
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        ) 