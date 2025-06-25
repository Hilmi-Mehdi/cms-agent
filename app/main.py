"""Main FastAPI application for the SMS-Agent."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.routers import agent, health, search
from app.utils.ai_client import ai_client

# --- Logging Configuration ---
# Set up logging to display INFO level messages
logging.basicConfig(level=settings.log_level.upper())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting SMS-Agent...")
    
    # Test AI connections
    try:
        connection_status = await ai_client.test_connections()
        print(f"AI Provider Status: {connection_status}")
    except Exception as e:
        print(f"Warning: Could not test AI connections: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SMS-Agent...")


# Create FastAPI app
app = FastAPI(
    title="SMS-Agent",
    description="Science Made Simple Agent - Intelligent course content analysis and generation using OpenAI and Google AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(agent.router, prefix=settings.api_prefix, tags=["Agent"])
app.include_router(search.router, prefix=settings.api_prefix, tags=["Search"])


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "SMS-Agent",
        "version": "1.0.0",
        "description": "Science Made Simple Agent - Intelligent course content analysis and generation",
        "endpoints": {
            "health": "/health",
            "agent": f"{settings.api_prefix}/agent",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    ) 