from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from api.routes import router as api_router
from core.config import settings
from services.langsmith_client import LangSmithClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Deep Research AI Agent",
    description="Autonomous research agent for comprehensive investigations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Initialize LangSmith client
langsmith_client = LangSmithClient()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await langsmith_client.initialize()
    print("Deep Research Agent Backend Started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await langsmith_client.cleanup()

@app.get("/")
async def root():
    return {
        "message": "Deep Research AI Agent API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Deep Research Agent API",
        "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp in production
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )