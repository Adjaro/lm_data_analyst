from fastapi import FastAPI
from .config import settings
from .api.routes import router as api_router
from .database import init_db

app = FastAPI(
    title="Data Analysis API",
    description="API pour l'analyse de données avec IA",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    init_db() 