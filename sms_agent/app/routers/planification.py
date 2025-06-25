from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict

from ..agent.planification_agent import PlanificationAgent

router = APIRouter()

# In-memory store for agent instances. In a real application, you might use a more persistent store.
agent_instances: Dict[str, PlanificationAgent] = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class StartChatResponse(BaseModel):
    session_id: str
    initial_message: str

@router.post("/planification/start", response_model=StartChatResponse)
async def start_planification_chat():
    """
    Starts a new planification chat session.
    """
    agent = PlanificationAgent()
    agent_instances[agent.agent_id] = agent
    
    initial_message = agent.process_message("") # Start the conversation
    
    return StartChatResponse(session_id=agent.agent_id, initial_message=initial_message)

@router.post("/planification/chat", response_model=ChatResponse)
async def chat_with_planification_agent(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Handles a message in a planification chat session.
    """
    agent = agent_instances.get(request.session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    response = agent.process_message(request.message)

    # Example of how to run agenda generation in the background
    # if agent.state == "generating_plan":
    #     background_tasks.add_task(agent._generate_plan)
    #     response = "I've received your preferences. I'm now generating your personalized study plan. I'll let you know when it's ready!"
    
    return ChatResponse(response=response)

@router.get("/planification/plan/{session_id}")
async def get_study_plan(session_id: str):
    """
    Retrieves the generated study plan for a session.
    """
    agent = agent_instances.get(session_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    if agent.state != "plan_generated":
        raise HTTPException(status_code=400, detail="Study plan has not been generated yet.")

    plan = agent.get_plan()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
        
    return plan.model_dump()