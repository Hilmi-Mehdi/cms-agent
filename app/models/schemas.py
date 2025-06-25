"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Agent processing status enumeration."""
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class Intent(str, Enum):
    """User intent classification."""
    ANALYZE_COURSE = "analyze_course"
    PROCESS_EXAM = "process_exam"
    MATCH_CONTENT = "match_content"
    OPTIMIZE_ANALYSIS = "optimize_analysis"
    GENERATE_CONTENT = "generate_content"


class AIProvider(str, Enum):
    """Supported AI model providers."""
    OPENAI = "openai"
    GOOGLE = "google"


class AgentRequest(BaseModel):
    """Request model for agent interactions."""
    user_query: str = Field(..., description="User's natural language request")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    files: Optional[List[str]] = Field(default=[], description="List of file paths to process")
    preferred_provider: Optional[AIProvider] = Field(default=None, description="Preferred AI provider")
    target_audience: Optional[str] = Field(default="general", description="Target audience for content")
    custom_requirements: Optional[Dict[str, Any]] = Field(default={}, description="Custom analysis requirements")


class AgentResponse(BaseModel):
    """Response model for agent interactions."""
    session_id: str = Field(..., description="Unique session identifier")
    response: str = Field(..., description="Agent's natural language response")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured data output")
    execution_summary: Optional[str] = Field(default=None, description="Summary of execution steps")
    agent_reasoning: Optional[str] = Field(default=None, description="Agent's reasoning process")
    suggested_follow_ups: Optional[List[str]] = Field(default=[], description="Suggested next actions")
    success: bool = Field(..., description="Whether the request was successful")
    processing_time: Optional[float] = Field(default=None, description="Total processing time in seconds")
    cache_hit: bool = Field(default=False, description="Whether response came from cache")
    errors: Optional[List[str]] = Field(default=[], description="Any errors encountered")


class TaskResult(BaseModel):
    """Result of a task execution."""
    task_id: str
    tool_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    suggested_next_tools: Optional[List[str]] = []
    quality_score: Optional[float] = None


class ToolResult(BaseModel):
    """Result from tool execution."""
    success: bool = Field(..., description="Whether tool execution was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Tool output data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    tool_name: Optional[str] = Field(default=None, description="Name of the executed tool")
    suggested_next_tools: Optional[List[str]] = Field(default=[], description="Recommended follow-up tools")
    agent_notes: Optional[str] = Field(default=None, description="Agent observations about the execution")


class SessionInfo(BaseModel):
    """Information about an agent session."""
    session_id: str
    user_id: str
    user_query: str
    intent: Optional[str] = None
    processing_status: ProcessingStatus
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_tasks: int = 0


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    dependencies: Dict[str, bool] = {}


class CourseAnalysis(BaseModel):
    """Structured course analysis result."""
    title: Optional[str] = None
    description: Optional[str] = None
    key_concepts: List[str] = []
    learning_objectives: List[str] = []
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[str] = None
    prerequisites: List[str] = []
    target_audience: Optional[str] = None
    content_structure: Dict[str, Any] = {}
    assessment_items: List[Dict[str, Any]] = []


class ExamAnalysis(BaseModel):
    """Structured exam analysis result."""
    exam_title: Optional[str] = None
    question_count: int = 0
    question_types: Dict[str, int] = {}
    topics_covered: List[str] = []
    difficulty_distribution: Dict[str, int] = {}
    estimated_duration: Optional[str] = None
    questions: List[Dict[str, Any]] = []


class ContentMatchResult(BaseModel):
    """Result of matching course content with exam questions."""
    match_score: float = Field(..., ge=0.0, le=1.0, description="Overall match score")
    covered_topics: List[str] = []
    missing_topics: List[str] = []
    recommendations: List[str] = []
    detailed_matches: List[Dict[str, Any]] = [] 