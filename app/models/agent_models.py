"""Internal agent models for session and task management."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.models.schemas import ProcessingStatus, TaskStatus


class AgentTask(BaseModel):
    """Internal model for agent tasks."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = Field(..., description="Type of task to execute")
    description: str = Field(..., description="Human-readable task description")
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default={}, description="Parameters for tool execution")
    dependencies: List[str] = Field(default=[], description="List of task IDs this task depends on")
    priority: int = Field(default=1, description="Task priority (lower = higher priority)")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task execution result")
    error_message: Optional[str] = Field(default=None, description="Error message if task failed")
    agent_reasoning: Optional[str] = Field(default=None, description="Agent's reasoning for this task")
    next_actions: Optional[List[str]] = Field(default=[], description="Suggested follow-up actions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    execution_start: Optional[datetime] = Field(default=None)
    execution_end: Optional[datetime] = Field(default=None)
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class AgentSession(BaseModel):
    """Internal model for agent sessions."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User identifier")
    user_query: str = Field(..., description="Original user request")
    intent: str = Field(default="", description="Classified user intent")
    current_task: Optional[str] = Field(default=None, description="Currently executing task ID")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PLANNING)
    context: Dict[str, Any] = Field(default={}, description="Session context and metadata")
    task_queue: List[AgentTask] = Field(default=[], description="Pending tasks")
    completed_tasks: List[AgentTask] = Field(default=[], description="Completed tasks")
    available_tools: List[str] = Field(default=[], description="Tools available for this session")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    session_summary: Optional[str] = Field(default=None, description="Session summary")


class ToolExecution(BaseModel):
    """Model for detailed tool execution logging."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Parent session ID")
    task_id: str = Field(..., description="Parent task ID")
    tool_name: str = Field(..., description="Name of executed tool")
    parameters: Dict[str, Any] = Field(..., description="Tool execution parameters")
    result: Dict[str, Any] = Field(..., description="Tool execution result")
    success: bool = Field(..., description="Whether execution was successful")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    agent_reasoning: Optional[str] = Field(default=None, description="Agent's reasoning")
    next_actions: List[str] = Field(default=[], description="Suggested next actions")
    quality_score: Optional[float] = Field(default=None, description="Quality assessment score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskPlan(BaseModel):
    """Model for multi-step task execution plan."""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Associated session ID")
    intent: str = Field(..., description="Primary intent being addressed")
    description: str = Field(..., description="Plan description")
    tasks: List[AgentTask] = Field(..., description="Ordered list of tasks")
    estimated_duration: Optional[float] = Field(default=None, description="Estimated execution time")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    agent_reasoning: Optional[str] = Field(default=None, description="Agent's planning reasoning")


class UserIntent(BaseModel):
    """Model for analyzed user intent."""
    primary_intent: str = Field(..., description="Primary classified intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification")
    secondary_intents: List[str] = Field(default=[], description="Secondary intents detected")
    extracted_entities: Dict[str, Any] = Field(default={}, description="Extracted entities from query")
    context_requirements: List[str] = Field(default=[], description="Required context for processing")
    suggested_tools: List[str] = Field(default=[], description="Recommended tools for this intent")
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Query complexity assessment")


class ValidationResult(BaseModel):
    """Model for result validation."""
    validation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(..., description="Associated session ID")
    overall_quality: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    needs_improvement: bool = Field(..., description="Whether results need improvement")
    validation_notes: str = Field(..., description="Detailed validation notes")
    specific_issues: List[str] = Field(default=[], description="Specific issues identified")
    improvement_suggestions: List[str] = Field(default=[], description="Suggested improvements")
    validated_results: Dict[str, Any] = Field(..., description="Validated result data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CacheEntry(BaseModel):
    """Model for content cache entries."""
    cache_key: str = Field(..., description="Unique cache key")
    content_hash: str = Field(..., description="Hash of the original content")
    analysis_type: str = Field(..., description="Type of analysis performed")
    content_metadata: Dict[str, Any] = Field(..., description="Metadata about original content")
    analysis_result: Dict[str, Any] = Field(..., description="Cached analysis result")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Cache expiration time")
    usage_count: int = Field(default=0, description="Number of times cache was accessed")
    last_accessed: datetime = Field(default_factory=datetime.utcnow) 