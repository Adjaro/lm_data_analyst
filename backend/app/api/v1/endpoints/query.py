from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ....db.base import get_db
from ....services.ai_service import AIService
from ....core.logging import get_logger
from pydantic import BaseModel, Field, validator
from sqlalchemy.exc import SQLAlchemyError
import time
from functools import wraps

router = APIRouter()
logger = get_logger(__name__)
ai_service = AIService()

def rate_limit(max_requests: int = 100, window: int = 3600):
    """Décorateur pour limiter le nombre de requêtes par IP."""
    requests = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()
            
            # Nettoie les anciennes requêtes
            requests[client_ip] = [t for t in requests.get(client_ip, []) 
                                 if current_time - t < window]
            
            # Vérifie la limite
            if len(requests.get(client_ip, [])) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
            
            # Ajoute la nouvelle requête
            requests.setdefault(client_ip, []).append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=500)
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

    @validator('prompt')
    def validate_prompt(cls, v):
        """Valide le contenu du prompt."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace")
        if len(v.split()) < 2:
            raise ValueError("Prompt must contain at least 2 words")
        return v

class QueryResponse(BaseModel):
    data: List[Dict[str, Any]]
    visualization_type: str
    title: str
    sql_query: str
    total_count: int
    page: int
    page_size: int
    total_pages: int
    execution_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
    database_status: str
    ai_service_status: str
    uptime: float

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Vérifie la santé du service et de ses dépendances."""
    start_time = time.time()
    
    try:
        # Vérifie la base de données
        db.execute("SELECT 1")
        db_status = "healthy"
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    # Vérifie le service AI
    try:
        ai_service.determine_visualization_type("test")
        ai_status = "healthy"
    except Exception as e:
        logger.error(f"AI service health check failed: {str(e)}")
        ai_status = "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" and ai_status == "healthy" else "degraded",
        version="1.0.0",
        database_status=db_status,
        ai_service_status=ai_status,
        uptime=time.time() - start_time
    )

@router.post("/query", response_model=QueryResponse)
@rate_limit(max_requests=100, window=3600)
async def process_query(
    request: Request,
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Traite une requête d'analyse de données."""
    start_time = time.time()
    
    try:
        logger.info(f"Processing query from {request.client.host}: {query_request.prompt}")
        
        # Génère la requête SQL
        sql_query = ai_service.generate_sql_query(query_request.prompt)
        
        # Calcule l'offset pour la pagination
        offset = (query_request.page - 1) * query_request.page_size
        
        # Ajoute la pagination à la requête SQL
        paginated_sql = f"""
        WITH base_query AS (
            {sql_query}
        )
        SELECT * FROM base_query
        LIMIT {query_request.page_size}
        OFFSET {offset}
        """
        
        # Exécute la requête paginée
        result = db.execute(paginated_sql)
        data = [dict(zip([col[0] for col in result.cursor.description], row)) 
                for row in result.fetchall()]
        
        # Compte le nombre total de résultats
        count_sql = f"SELECT COUNT(*) as total FROM ({sql_query}) as count_query"
        total_count = db.execute(count_sql).scalar()
        
        # Calcule le nombre total de pages
        total_pages = (total_count + query_request.page_size - 1) // query_request.page_size
        
        # Détermine le type de visualisation
        viz_type = ai_service.determine_visualization_type(query_request.prompt)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            data=data,
            visualization_type=viz_type,
            title=query_request.prompt,
            sql_query=sql_query,
            total_count=total_count,
            page=query_request.page,
            page_size=query_request.page_size,
            total_pages=total_pages,
            execution_time=execution_time
        )
        
    except ValueError as e:
        logger.error(f"Invalid query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 