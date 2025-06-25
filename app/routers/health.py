"""Health check endpoints for the AI agent system."""

from fastapi import APIRouter
from datetime import datetime

from app.models.schemas import HealthCheck
from app.utils.ai_client import ai_client
from app.tools.base_tool import tool_registry

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """Basic health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.get("/detailed", response_model=HealthCheck)
async def detailed_health_check():
    """Detailed health check with dependency status."""
    dependencies = {}
    
    try:
        # Test AI provider connections
        ai_status = await ai_client.test_connections()
        dependencies.update(ai_status)
    except Exception as e:
        dependencies["ai_providers"] = False
    
    # Check tool registry
    dependencies["tool_registry"] = len(tool_registry.available_tools) > 0
    dependencies["available_tools"] = tool_registry.available_tools
    
    # Determine overall status
    overall_status = "healthy" if all(dependencies.values()) else "degraded"
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        dependencies=dependencies
    ) 