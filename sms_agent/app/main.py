from fastapi import FastAPI
from .routers import agent, health, search, planification

app = FastAPI(
    title="AI Course Management Agent",
    description="An advanced AI agent for managing university courses, powered by large language models.",
    version="1.0.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(agent.router, prefix="/api/v1", tags=["Agent"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(planification.router, prefix="/api/v1", tags=["Planification"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Course Management Agent API"}