# AI Course Analysis Agent MVP - DynamoDB Technical Specification

## Overview

Autonomous AI agent system that intelligently analyzes educational content using OpenAI function calling with DynamoDB as the persistence layer. The agent makes independent decisions about processing strategies, selects appropriate tools, and orchestrates complex multi-step workflows for course and exam analysis.

## Agent Architecture

### Core Agent Loop
```python
class CourseAnalysisAgent:
    async def process_request(self, user_request: str, context: Dict) -> AgentResponse:
        """Main agent decision loop with DynamoDB persistence"""
        # 1. Analyze user intent and available context
        # 2. Plan multi-step approach using available tools
        # 3. Execute tools in intelligent sequence
        # 4. Validate results and decide on next actions
        # 5. Generate comprehensive response
        # 6. Persist session state to DynamoDB
```

### Agent Components
- **Intent Analyzer**: Understands user requests and determines goals
- **Task Planner**: Creates multi-step execution plans
- **Tool Orchestrator**: Selects and executes appropriate tools
- **Context Manager**: Maintains conversation and processing state in DynamoDB
- **Quality Controller**: Validates outputs and triggers improvements
- **Response Generator**: Synthesizes results into coherent responses

## Technology Stack

- **Framework**: FastAPI with async/await
- **AI Model**: OpenAI GPT-4.1-nano with function calling
- **Database**: AWS DynamoDB with boto3
- **Agent State**: DynamoDB with TTL for session management
- **Validation**: Pydantic v2
- **AWS Integration**: boto3, aioboto3 for async operations

## Project Structure

```
ai-course-agent/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                 # Environment configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── dynamodb_client.py    # DynamoDB client setup
│   │   ├── models.py             # DynamoDB table models
│   │   └── repositories.py       # Data access layer
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core_agent.py         # Main agent orchestrator
│   │   ├── intent_analyzer.py    # Request understanding
│   │   ├── task_planner.py       # Multi-step planning
│   │   ├── context_manager.py    # DynamoDB state management
│   │   └── response_generator.py # Output synthesis
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py          # Abstract tool interface
│   │   ├── tool_registry.py      # Tool management
│   │   ├── file_processor.py     # File handling tool
│   │   ├── content_analyzer.py   # Content analysis tool
│   │   ├── structure_extractor.py # Course structure tool
│   │   ├── learning_path_builder.py # Learning progression tool
│   │   ├── exam_processor.py     # Exam analysis tool
│   │   ├── exercise_matcher.py   # Course-exam matching tool
│   │   ├── quality_assessor.py   # Analysis validation tool
│   │   └── prompt_optimizer.py   # Prompt improvement tool
│   ├── models/
│   │   ├── schemas.py            # Pydantic models
│   │   ├── dynamodb_models.py    # DynamoDB item models
│   │   └── agent_models.py       # Agent-specific models
│   ├── routers/
│   │   ├── agent.py              # Agent interaction endpoints
│   │   └── health.py             # System health
│   └── utils/
│       ├── logging.py            # Logging setup
│       ├── exceptions.py         # Custom exceptions
│       └── ai_client.py          # OpenAI client
├── infrastructure/
│   ── dynamodb_tables.yaml      # DynamoDB table definitions
├── prompts/
│   ├── agent_system.yaml         # Core agent prompts
│   ├── tool_selection.yaml       # Tool choice prompts
│   └── task_planning.yaml        # Planning prompts
├── requirements.txt
├── .env
└── README.md
```

## DynamoDB Schema Design

### Table Structure

#### AgentSessions Table
```python
# Primary Table: agent-sessions
{
    "PK": "SESSION#<session_id>",           # Partition Key
    "SK": "METADATA",                        # Sort Key
    "GSI1PK": "USER#<user_id>",             # Global Secondary Index
    "GSI1SK": "SESSION#<timestamp>",         # GSI Sort Key
    "session_id": "uuid-string",
    "user_id": "user-identifier",
    "user_query": "original user request",
    "intent": "analyze_course|process_exam|match_content|optimize_analysis",
    "current_task": "task-id or null",
    "processing_status": "planning|executing|validating|completed|failed",
    "context": {
        "files": ["file1.pptx", "file2.pdf"],
        "target_audience": "beginners",
        "custom_requirements": {}
    },
    "available_tools": ["file_processor", "content_analyzer", ...],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "expires_at": 1705312200,                # TTL for automatic cleanup
    "session_summary": "Brief description of session goals and outcomes"
}
```

#### Tasks Table
```python
# Tasks within sessions
{
    "PK": "SESSION#<session_id>",           # Partition Key
    "SK": "TASK#<task_id>",                 # Sort Key
    "GSI1PK": "STATUS#<status>",            # For querying by status
    "GSI1SK": "PRIORITY#<priority>#<created_at>", # For priority ordering
    "task_id": "uuid-string",
    "task_type": "file_processing|content_analysis|quality_check",
    "description": "Human readable task description",
    "tool_name": "content_analyzer",
    "parameters": {
        "content": "...",
        "analysis_type": "comprehensive"
    },
    "dependencies": ["task-id-1", "task-id-2"],  # Tasks this depends on
    "priority": 1,                          # Lower = higher priority
    "status": "pending|executing|completed|failed",
    "result": {
        "success": true,
        "data": {...},
        "execution_time": 12.5
    },
    "error_message": "Error details if failed",
    "agent_reasoning": "Why agent chose this approach",
    "next_actions": ["suggested follow-up actions"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:32:00Z",
    "execution_start": "2024-01-15T10:31:00Z",
    "execution_end": "2024-01-15T10:32:00Z"
}
```

#### Tool Executions Table
```python
# Detailed tool execution logs
{
    "PK": "SESSION#<session_id>",           # Partition Key
    "SK": "EXECUTION#<execution_id>",       # Sort Key
    "GSI1PK": "TOOL#<tool_name>",          # For tool performance analysis
    "GSI1SK": "TIME#<timestamp>",           # For chronological queries
    "execution_id": "uuid-string",
    "task_id": "parent-task-id",
    "tool_name": "content_analyzer",
    "parameters": {
        "input_parameters": "as provided to tool"
    },
    "result": {
        "success": true,
        "data": "tool output",
        "suggested_next_tools": ["quality_assessor"],
        "agent_notes": "Tool-specific observations"
    },
    "execution_time": 15.7,
    "success": true,
    "error_message": null,
    "agent_reasoning": "Why this tool was selected",
    "quality_score": 0.92,
    "timestamp": "2024-01-15T10:31:30Z"
}
```

#### Content Cache Table
```python
# Cache processed content to avoid reprocessing
{
    "PK": "CONTENT#<content_hash>",         # Partition Key
    "SK": "ANALYSIS#<analysis_type>",       # Sort Key
    "content_hash": "sha256-hash-of-content",
    "analysis_type": "comprehensive|structure|concepts",
    "content_metadata": {
        "file_name": "course.pptx",
        "file_size": 2048576,
        "content_type": "presentation"
    },
    "analysis_result": {
        "key_concepts": [...],
        "difficulty_level": "intermediate",
        "learning_objectives": [...]
    },
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": 1705398600,               # TTL for cache expiration
    "usage_count": 3,
    "last_accessed": "2024-01-15T15:20:00Z"
}
```

### DynamoDB Table Definitions

```yaml
# infrastructure/dynamodb_tables.yaml
Tables:
  AgentSessionsTable:
    TableName: ai-course-agent-sessions
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: PK
        AttributeType: S
      - AttributeName: SK
        AttributeType: S
      - AttributeName: GSI1PK
        AttributeType: S
      - AttributeName: GSI1SK
        AttributeType: S
    KeySchema:
      - AttributeName: PK
        KeyType: HASH
      - AttributeName: SK
        KeyType: RANGE
    GlobalSecondaryIndexes:
      - IndexName: GSI1
        KeySchema:
          - AttributeName: GSI1PK
            KeyType: HASH
          - AttributeName: GSI1SK
            KeyType: RANGE
        Projection:
          ProjectionType: ALL
    TimeToLiveSpecification:
      AttributeName: expires_at
      Enabled: true
    PointInTimeRecoverySpecification:
      PointInTimeRecoveryEnabled: true

  ContentCacheTable:
    TableName: ai-course-agent-content-cache
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: PK
        AttributeType: S
      - AttributeName: SK
        AttributeType: S
    KeySchema:
      - AttributeName: PK
        KeyType: HASH
      - AttributeName: SK
        KeyType: RANGE
    TimeToLiveSpecification:
      AttributeName: expires_at
      Enabled: true
```

## DynamoDB Integration Implementation

### DynamoDB Client Setup
```python
# app/database/dynamodb_client.py
import boto3
import aioboto3
from botocore.config import Config
from typing import Optional
import os

class DynamoDBClient:
    def __init__(self):
        self.config = Config(
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )
        
        # Sync client for initialization
        self.dynamodb = boto3.resource(
            'dynamodb',
            config=self.config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Table references
        self.sessions_table = self.dynamodb.Table('ai-course-agent-sessions')
        self.content_cache_table = self.dynamodb.Table('ai-course-agent-content-cache')
    
    async def get_async_client(self):
        """Get async DynamoDB client for concurrent operations"""
        session = aioboto3.Session()
        return session.resource(
            'dynamodb',
            config=self.config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

# Global client instance
dynamodb_client = DynamoDBClient()
```

### Agent Session Repository
```python
# app/database/repositories.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import json
from boto3.dynamodb.conditions import Key, Attr
from app.models.agent_models import AgentSession, AgentTask, ToolExecution

class AgentSessionRepository:
    def __init__(self, dynamodb_client: DynamoDBClient):
        self.client = dynamodb_client
        self.table = dynamodb_client.sessions_table
    
    async def create_session(self, user_id: str, user_query: str, context: Dict = None) -> AgentSession:
        """Create new agent session with TTL"""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = int((now + timedelta(hours=24)).timestamp())  # 24 hour TTL
        
        session_item = {
            'PK': f'SESSION#{session_id}',
            'SK': 'METADATA',
            'GSI1PK': f'USER#{user_id}',
            'GSI1SK': f'SESSION#{now.isoformat()}',
            'session_id': session_id,
            'user_id': user_id,
            'user_query': user_query,
            'intent': '',
            'current_task': None,
            'processing_status': 'planning',
            'context': context or {},
            'available_tools': [],
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'expires_at': expires_at
        }
        
        self.table.put_item(Item=session_item)
        
        return AgentSession(
            session_id=session_id,
            user_id=user_id,
            user_query=user_query,
            intent='',
            processing_status='planning',
            context=context or {},
            task_queue=[],
            completed_tasks=[],
            available_tools=[],
            created_at=now,
            updated_at=now
        )
    
    async def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Retrieve session with all associated tasks"""
        try:
            # Get session metadata
            response = self.table.get_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'METADATA'
                }
            )
            
            if 'Item' not in response:
                return None
                
            session_data = response['Item']
            
            # Get all tasks for this session
            tasks_response = self.table.query(
                KeyConditionExpression=Key('PK').eq(f'SESSION#{session_id}') & 
                                     Key('SK').begins_with('TASK#')
            )
            
            # Convert tasks to AgentTask objects
            tasks = []
            completed_tasks = []
            for item in tasks_response['Items']:
                task = self._item_to_task(item)
                if task.status in ['pending', 'executing']:
                    tasks.append(task)
                else:
                    completed_tasks.append(task)
            
            return AgentSession(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                user_query=session_data['user_query'],
                intent=session_data.get('intent', ''),
                current_task=session_data.get('current_task'),
                processing_status=session_data['processing_status'],
                context=session_data.get('context', {}),
                task_queue=tasks,
                completed_tasks=completed_tasks,
                available_tools=session_data.get('available_tools', []),
                created_at=datetime.fromisoformat(session_data['created_at']),
                updated_at=datetime.fromisoformat(session_data['updated_at'])
            )
            
        except Exception as e:
            print(f"Error retrieving session {session_id}: {e}")
            return None
    
    async def update_session(self, session: AgentSession) -> bool:
        """Update session metadata"""
        try:
            now = datetime.utcnow()
            
            self.table.update_item(
                Key={
                    'PK': f'SESSION#{session.session_id}',
                    'SK': 'METADATA'
                },
                UpdateExpression="""
                    SET intent = :intent,
                        current_task = :current_task,
                        processing_status = :status,
                        context = :context,
                        available_tools = :tools,
                        updated_at = :updated_at
                """,
                ExpressionAttributeValues={
                    ':intent': session.intent,
                    ':current_task': session.current_task,
                    ':status': session.processing_status,
                    ':context': session.context,
                    ':tools': session.available_tools,
                    ':updated_at': now.isoformat()
                }
            )
            return True
        except Exception as e:
            print(f"Error updating session {session.session_id}: {e}")
            return False
    
    async def add_task(self, session_id: str, task: AgentTask) -> bool:
        """Add task to session"""
        try:
            task_item = {
                'PK': f'SESSION#{session_id}',
                'SK': f'TASK#{task.task_id}',
                'GSI1PK': f'STATUS#{task.status}',
                'GSI1SK': f'PRIORITY#{task.priority:03d}#{task.created_at.isoformat()}',
                'task_id': task.task_id,
                'task_type': task.task_type,
                'description': task.description,
                'tool_name': task.tool_name,
                'parameters': task.parameters,
                'dependencies': task.dependencies,
                'priority': task.priority,
                'status': task.status,
                'result': task.result,
                'agent_reasoning': getattr(task, 'agent_reasoning', ''),
                'next_actions': getattr(task, 'next_actions', []),
                'created_at': task.created_at.isoformat(),
                'updated_at': task.created_at.isoformat()
            }
            
            self.table.put_item(Item=task_item)
            return True
        except Exception as e:
            print(f"Error adding task {task.task_id}: {e}")
            return False
    
    async def update_task(self, session_id: str, task: AgentTask) -> bool:
        """Update task status and result"""
        try:
            now = datetime.utcnow()
            
            self.table.update_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': f'TASK#{task.task_id}'
                },
                UpdateExpression="""
                    SET #status = :status,
                        #result = :result,
                        updated_at = :updated_at,
                        GSI1PK = :gsi1pk
                """,
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#result': 'result'
                },
                ExpressionAttributeValues={
                    ':status': task.status,
                    ':result': task.result,
                    ':updated_at': now.isoformat(),
                    ':gsi1pk': f'STATUS#{task.status}'
                }
            )
            return True
        except Exception as e:
            print(f"Error updating task {task.task_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[AgentSession]:
        """Get recent sessions for a user"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'USER#{user_id}'),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            sessions = []
            for item in response['Items']:
                session = self._item_to_session_summary(item)
                sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"Error getting user sessions for {user_id}: {e}")
            return []
    
    def _item_to_task(self, item: Dict) -> AgentTask:
        """Convert DynamoDB item to AgentTask"""
        return AgentTask(
            task_id=item['task_id'],
            task_type=item['task_type'],
            description=item['description'],
            tool_name=item['tool_name'],
            parameters=item.get('parameters', {}),
            dependencies=item.get('dependencies', []),
            priority=item.get('priority', 1),
            status=item['status'],
            result=item.get('result'),
            execution_time=item.get('execution_time'),
            created_at=datetime.fromisoformat(item['created_at'])
        )
    
    def _item_to_session_summary(self, item: Dict) -> AgentSession:
        """Convert DynamoDB item to AgentSession summary"""
        return AgentSession(
            session_id=item['session_id'],
            user_id=item['user_id'],
            user_query=item['user_query'],
            intent=item.get('intent', ''),
            processing_status=item['processing_status'],
            context=item.get('context', {}),
            task_queue=[],
            completed_tasks=[],
            available_tools=item.get('available_tools', []),
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )
```

### Content Cache Repository
```python
class ContentCacheRepository:
    def __init__(self, dynamodb_client: DynamoDBClient):
        self.client = dynamodb_client
        self.table = dynamodb_client.content_cache_table
    
    async def get_cached_analysis(self, content_hash: str, analysis_type: str) -> Optional[Dict]:
        """Retrieve cached content analysis"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'CONTENT#{content_hash}',
                    'SK': f'ANALYSIS#{analysis_type}'
                }
            )
            
            if 'Item' in response:
                item = response['Item']
                
                # Update usage statistics
                self.table.update_item(
                    Key={
                        'PK': f'CONTENT#{content_hash}',
                        'SK': f'ANALYSIS#{analysis_type}'
                    },
                    UpdateExpression='ADD usage_count :inc SET last_accessed = :now',
                    ExpressionAttributeValues={
                        ':inc': 1,
                        ':now': datetime.utcnow().isoformat()
                    }
                )
                
                return item.get('analysis_result')
            
            return None
        except Exception as e:
            print(f"Error retrieving cached analysis: {e}")
            return None
    
    async def cache_analysis(self, content_hash: str, analysis_type: str, 
                           content_metadata: Dict, analysis_result: Dict, 
                           cache_duration_hours: int = 168) -> bool:  # 1 week default
        """Cache content analysis result"""
        try:
            now = datetime.utcnow()
            expires_at = int((now + timedelta(hours=cache_duration_hours)).timestamp())
            
            cache_item = {
                'PK': f'CONTENT#{content_hash}',
                'SK': f'ANALYSIS#{analysis_type}',
                'content_hash': content_hash,
                'analysis_type': analysis_type,
                'content_metadata': content_metadata,
                'analysis_result': analysis_result,
                'created_at': now.isoformat(),
                'expires_at': expires_at,
                'usage_count': 1,
                'last_accessed': now.isoformat()
            }
            
            self.table.put_item(Item=cache_item)
            return True
        except Exception as e:
            print(f"Error caching analysis: {e}")
            return False
```

### Context Manager with DynamoDB
```python
# app/agent/context_manager.py
from app.database.repositories import AgentSessionRepository, ContentCacheRepository
from app.database.dynamodb_client import dynamodb_client

class ContextManager:
    def __init__(self):
        self.session_repo = AgentSessionRepository(dynamodb_client)
        self.cache_repo = ContentCacheRepository(dynamodb_client)
    
    async def get_or_create_session(self, session_id: str, user_query: str, 
                                  context: Dict = None, user_id: str = "default") -> AgentSession:
        """Get existing session or create new one"""
        if session_id:
            session = await self.session_repo.get_session(session_id)
            if session:
                return session
        
        # Create new session
        return await self.session_repo.create_session(user_id, user_query, context)
    
    async def save_session(self, session: AgentSession) -> bool:
        """Persist session state to DynamoDB"""
        return await self.session_repo.update_session(session)
    
    async def add_task_to_session(self, session_id: str, task: AgentTask) -> bool:
        """Add task to session queue"""
        return await self.session_repo.add_task(session_id, task)
    
    async def update_task_status(self, session_id: str, task: AgentTask) -> bool:
        """Update task execution status"""
        return await self.session_repo.update_task(session_id, task)
    
    async def get_cached_content_analysis(self, content_hash: str, analysis_type: str) -> Optional[Dict]:
        """Check for cached analysis results"""
        return await self.cache_repo.get_cached_analysis(content_hash, analysis_type)
    
    async def cache_content_analysis(self, content_hash: str, analysis_type: str,
                                   content_metadata: Dict, analysis_result: Dict) -> bool:
        """Cache analysis results for future use"""
        return await self.cache_repo.cache_analysis(
            content_hash, analysis_type, content_metadata, analysis_result
        )
```

## Updated Agent Models for DynamoDB

```python
# app/models/agent_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class AgentSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_query: str
    intent: str = ""
    current_task: Optional[str] = None
    task_queue: List['AgentTask'] = Field(default_factory=list)
    completed_tasks: List['AgentTask'] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    available_tools: List[str] = Field(default_factory=list)
    processing_status: str = "planning"  # planning, executing, validating, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    session_summary: Optional[str] = None

class AgentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    description: str
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    priority: int = 1
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    agent_reasoning: str = ""
    next_actions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ToolExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    task_id: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    agent_reasoning: str
    next_actions: List[str] = Field(default_factory=list)
    quality_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Forward reference resolution
AgentSession.model_rebuild()
```

## Environment Configuration

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# DynamoDB Configuration
DYNAMODB_SESSIONS_TABLE=ai-course-agent-sessions
DYNAMODB_CONTENT_CACHE_TABLE=ai-course-agent-content-cache
DYNAMODB_ENDPOINT_URL=  # Leave empty for AWS, set for local development

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.1

# Agent Configuration
AGENT_MAX_ITERATIONS=10
AGENT_QUALITY_THRESHOLD=0.8
AGENT_AUTO_OPTIMIZATION=true
AGENT_SESSION_TIMEOUT=86400  # 24 hours in seconds

# Tool Configuration
MAX_CONCURRENT_TOOLS=3
TOOL_EXECUTION_TIMEOUT=300
ENABLE_AUTONOMOUS_RECOVERY=true

# File Processing
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE_MB=100

# Cache Configuration
CONTENT_CACHE_TTL_HOURS=168  # 1 week
ENABLE_CONTENT_CACHING=true
```

## Required AWS Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/ai-course-agent-sessions",
        "arn:aws:dynamodb:*:*:table/ai-course-agent-sessions/index/*",
        "arn:aws:dynamodb:*:*:table/ai-course-agent-content-cache"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:DescribeTimeToLive"
      ],
      "Resource": "*"
    }
  ]
}
```

## Updated Dependencies

```python
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
boto3==1.34.0
aioboto3==12.0.0
openai==1.3.7
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
Pillow==10.1.0
PyPDF2==3.0.1
python-pptx==0.6.22
aiofiles==23.2.1
httpx==0.25.2
pyyaml==6.0.1
```

## DynamoDB Performance Optimizations

### Batch Operations
```python
# app/database/repositories.py (continued)
from boto3.dynamodb.conditions import Key
import asyncio
from typing import List

class AgentSessionRepository:
    # ... previous methods ...
    
    async def batch_get_tasks(self, session_id: str, task_ids: List[str]) -> List[AgentTask]:
        """Efficiently retrieve multiple tasks"""
        try:
            # Prepare batch get request
            request_items = {
                'ai-course-agent-sessions': {
                    'Keys': [
                        {
                            'PK': f'SESSION#{session_id}',
                            'SK': f'TASK#{task_id}'
                        } for task_id in task_ids
                    ]
                }
            }
            
            response = self.client.dynamodb.batch_get_item(RequestItems=request_items)
            
            tasks = []
            for item in response.get('Responses', {}).get('ai-course-agent-sessions', []):
                tasks.append(self._item_to_task(item))
            
            return tasks
        except Exception as e:
            print(f"Error batch getting tasks: {e}")
            return []
    
    async def batch_update_task_status(self, session_id: str, task_updates: List[Dict]) -> bool:
        """Batch update multiple task statuses"""
        try:
            # Use batch write for multiple updates
            with self.table.batch_writer() as batch:
                for update in task_updates:
                    batch.put_item(
                        Item={
                            'PK': f'SESSION#{session_id}',
                            'SK': f'TASK#{update["task_id"]}',
                            'status': update['status'],
                            'updated_at': datetime.utcnow().isoformat(),
                            **update.get('additional_fields', {})
                        }
                    )
            
            return True
        except Exception as e:
            print(f"Error batch updating tasks: {e}")
            return False
    
    async def get_pending_tasks_by_priority(self, session_id: str, limit: int = 10) -> List[AgentTask]:
        """Get pending tasks ordered by priority"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq('STATUS#pending'),
                FilterExpression=Attr('PK').eq(f'SESSION#{session_id}'),
                ScanIndexForward=True,  # Ascending priority (lower = higher priority)
                Limit=limit
            )
            
            tasks = []
            for item in response['Items']:
                tasks.append(self._item_to_task(item))
            
            return tasks
        except Exception as e:
            print(f"Error getting pending tasks: {e}")
            return []
```

### Connection Pooling and Async Operations
```python
# app/database/dynamodb_client.py (continued)
import asyncio
from contextlib import asynccontextmanager

class DynamoDBClient:
    def __init__(self):
        # ... previous initialization ...
        self._async_session_pool = None
        self._pool_size = int(os.getenv('DYNAMODB_POOL_SIZE', '10'))
    
    @asynccontextmanager
    async def get_async_resource(self):
        """Get async DynamoDB resource with connection pooling"""
        if not self._async_session_pool:
            await self._initialize_async_pool()
        
        session = aioboto3.Session()
        async with session.resource(
            'dynamodb',
            config=self.config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        ) as dynamodb:
            yield dynamodb
    
    async def _initialize_async_pool(self):
        """Initialize connection pool for async operations"""
        # Connection pool configuration
        self.config = Config(
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            max_pool_connections=self._pool_size
        )
```

## Enhanced Agent Implementation with DynamoDB

### Updated Core Agent
```python
# app/agent/core_agent.py
import asyncio
from typing import Dict, List, Any
from app.database.repositories import AgentSessionRepository, ContentCacheRepository
from app.models.agent_models import AgentSession, AgentTask, ToolExecution
from app.agent.context_manager import ContextManager
import hashlib
import json

class CourseAnalysisAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.ai_client = OpenAIClient(config.openai_api_key)
        self.tool_registry = ToolRegistry()
        self.context_manager = ContextManager()
        self.intent_analyzer = IntentAnalyzer()
        self.task_planner = TaskPlanner()
        self.response_generator = ResponseGenerator()
    
    async def process_request(self, user_request: str, session_id: str = None, 
                            context: Dict = None, user_id: str = "default") -> AgentResponse:
        """Main agent processing loop with DynamoDB persistence"""
        
        # Initialize or retrieve session from DynamoDB
        session = await self.context_manager.get_or_create_session(
            session_id, user_request, context, user_id
        )
        
        try:
            # Phase 1: Understand user intent
            intent = await self.intent_analyzer.analyze_intent(user_request, session.context)
            session.intent = intent.primary_intent
            await self.context_manager.save_session(session)
            
            # Phase 2: Check for cached results
            content_hash = self._generate_content_hash(user_request, context)
            cached_result = await self.context_manager.get_cached_content_analysis(
                content_hash, intent.primary_intent
            )
            
            if cached_result and self.config.enable_content_caching:
                return self._create_response_from_cache(cached_result, session)
            
            # Phase 3: Plan task sequence
            task_plan = await self.task_planner.create_plan(
                intent, session.context, self.tool_registry.available_tools
            )
            
            # Add tasks to DynamoDB
            for task in task_plan.tasks:
                await self.context_manager.add_task_to_session(session.session_id, task)
            
            session.processing_status = "executing"
            await self.context_manager.save_session(session)
            
            # Phase 4: Execute tasks with concurrent processing where possible
            execution_results = await self._execute_tasks_concurrently(session, task_plan.tasks)
            
            # Phase 5: Validate and improve results
            validation_result = await self._validate_results_autonomously(execution_results, session)
            
            if validation_result.needs_improvement:
                improvement_tasks = await self._plan_improvements(validation_result, session)
                improvement_results = await self._execute_tasks_concurrently(session, improvement_tasks)
                execution_results.extend(improvement_results)
            
            # Phase 6: Generate and cache response
            session.processing_status = "completed"
            await self.context_manager.save_session(session)
            
            response = await self.response_generator.generate_response(
                session.user_query, execution_results, session.context
            )
            
            # Cache successful results
            if response.success and self.config.enable_content_caching:
                await self.context_manager.cache_content_analysis(
                    content_hash, intent.primary_intent,
                    {"user_request": user_request, "context": context},
                    response.structured_data
                )
            
            return AgentResponse(
                session_id=session.session_id,
                response=response.content,
                data=response.structured_data,
                execution_summary=response.execution_summary,
                agent_reasoning=response.reasoning,
                suggested_follow_ups=response.follow_ups,
                success=True,
                processing_time=response.processing_time,
                cache_hit=False
            )
            
        except Exception as e:
            session.processing_status = "failed"
            await self.context_manager.save_session(session)
            error_response = await self._handle_error_autonomously(e, session)
            return error_response
    
    async def _execute_tasks_concurrently(self, session: AgentSession, 
                                        tasks: List[AgentTask]) -> List[ToolResult]:
        """Execute tasks concurrently where dependencies allow"""
        execution_results = []
        completed_task_ids = set()
        
        while tasks or any(task for task in session.task_queue if task.status == 'pending'):
            # Find tasks that can run concurrently (no unmet dependencies)
            ready_tasks = [
                task for task in tasks 
                if task.status == 'pending' and 
                all(dep_id in completed_task_ids for dep_id in task.dependencies)
            ]
            
            if not ready_tasks:
                break
            
            # Execute ready tasks concurrently (up to max_concurrent_tools)
            concurrent_tasks = ready_tasks[:self.config.max_concurrent_tools]
            
            # Create coroutines for concurrent execution
            task_coroutines = [
                self._execute_single_task(session, task) for task in concurrent_tasks
            ]
            
            # Execute tasks concurrently
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                task = concurrent_tasks[i]
                if isinstance(result, Exception):
                    # Handle task failure
                    task.status = 'failed'
                    task.result = {'error': str(result)}
                    await self.context_manager.update_task_status(session.session_id, task)
                else:
                    # Task succeeded
                    task.status = 'completed'
                    task.result = result.data
                    task.execution_time = result.execution_time
                    completed_task_ids.add(task.task_id)
                    execution_results.append(result)
                    await self.context_manager.update_task_status(session.session_id, task)
            
            # Remove completed/failed tasks from pending list
            tasks = [task for task in tasks if task.status == 'pending']
        
        return execution_results
    
    async def _execute_single_task(self, session: AgentSession, task: AgentTask) -> ToolResult:
        """Execute a single task with full instrumentation"""
        start_time = asyncio.get_event_loop().time()
        
        # Update task status to executing
        task.status = 'executing'
        await self.context_manager.update_task_status(session.session_id, task)
        
        try:
            tool = self.tool_registry.get_tool(task.tool_name)
            
            # Execute tool with timeout
            result = await asyncio.wait_for(
                tool.execute(task.parameters),
                timeout=self.config.tool_execution_timeout
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            result.execution_time = execution_time
            
            # Log execution to DynamoDB for performance monitoring
            await self._log_tool_execution(session.session_id, task, result)
            
            return result
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_result = ToolResult(
                success=False,
                error="Tool execution timeout",
                execution_time=execution_time,
                tool_name=task.tool_name
            )
            await self._log_tool_execution(session.session_id, task, error_result)
            raise Exception(f"Tool {task.tool_name} timed out after {self.config.tool_execution_timeout}s")
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_result = ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                tool_name=task.tool_name
            )
            await self._log_tool_execution(session.session_id, task, error_result)
            raise
    
    async def _log_tool_execution(self, session_id: str, task: AgentTask, result: ToolResult):
        """Log detailed tool execution for performance monitoring"""
        execution = ToolExecution(
            session_id=session_id,
            task_id=task.task_id,
            tool_name=task.tool_name,
            parameters=task.parameters,
            result=result.data if result.success else {"error": result.error},
            success=result.success,
            execution_time=result.execution_time,
            error_message=result.error if not result.success else None,
            agent_reasoning=getattr(result, 'agent_notes', ''),
            next_actions=getattr(result, 'suggested_next_tools', []),
            quality_score=getattr(result, 'quality_score', None)
        )
        
        # Store execution log in DynamoDB (could be separate table for analytics)
        # For now, we'll add it to the session table with EXECUTION# prefix
        try:
            item = {
                'PK': f'SESSION#{session_id}',
                'SK': f'EXECUTION#{execution.execution_id}',
                'GSI1PK': f'TOOL#{task.tool_name}',
                'GSI1SK': f'TIME#{execution.timestamp.isoformat()}',
                **execution.dict()
            }
            
            # Use the session repository's table for simplicity
            session_repo = self.context_manager.session_repo
            session_repo.table.put_item(Item=item)
            
        except Exception as e:
            print(f"Failed to log tool execution: {e}")
            # Don't fail the main process for logging issues
    
    def _generate_content_hash(self, user_request: str, context: Dict = None) -> str:
        """Generate hash for content caching"""
        content_to_hash = {
            'request': user_request,
            'context': context or {}
        }
        content_str = json.dumps(content_to_hash, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _create_response_from_cache(self, cached_result: Dict, session: AgentSession) -> AgentResponse:
        """Create response from cached analysis"""
        return AgentResponse(
            session_id=session.session_id,
            response=cached_result.get('summary', 'Analysis completed from cache'),
            data=cached_result,
            execution_summary="Retrieved from cache",
            agent_reasoning="Used cached analysis result",
            suggested_follow_ups=cached_result.get('follow_ups', []),
            success=True,
            processing_time=0.1,  # Minimal time for cache retrieval
            cache_hit=True
        )
```

## Monitoring and Analytics

### Performance Monitoring
```python
# app/utils/monitoring.py
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta
from app.database.repositories import AgentSessionRepository

class AgentPerformanceMonitor:
    def __init__(self, session_repo: AgentSessionRepository):
        self.session_repo = session_repo
    
    async def get_performance_metrics(self, hours_back: int = 24) -> Dict:
        """Get agent performance metrics from DynamoDB"""
        try:
            # Query recent executions
            since_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            response = self.session_repo.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').begins_with('TOOL#') &
                                     Key('GSI1SK').gte(f'TIME#{since_time.isoformat()}')
            )
            
            executions = response['Items']
            
            # Calculate metrics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.get('success', False)])
            avg_execution_time = sum(e.get('execution_time', 0) for e in executions) / max(total_executions, 1)
            
            # Tool performance breakdown
            tool_performance = {}
            for execution in executions:
                tool_name = execution.get('tool_name', 'unknown')
                if tool_name not in tool_performance:
                    tool_performance[tool_name] = {
                        'total': 0,
                        'successful': 0,
                        'avg_time': 0,
                        'times': []
                    }
                
                tool_performance[tool_name]['total'] += 1
                tool_performance[tool_name]['times'].append(execution.get('execution_time', 0))
                if execution.get('success', False):
                    tool_performance[tool_name]['successful'] += 1
            
            # Calculate averages
            for tool_data in tool_performance.values():
                tool_data['avg_time'] = sum(tool_data['times']) / len(tool_data['times'])
                tool_data['success_rate'] = tool_data['successful'] / tool_data['total']
                del tool_data['times']  # Remove raw times from response
            
            return {
                'period_hours': hours_back,
                'total_executions': total_executions,
                'success_rate': successful_executions / max(total_executions, 1),
                'avg_execution_time': avg_execution_time,
                'tool_performance': tool_performance,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return {}
    
    async def get_session_analytics(self, user_id: str = None, days_back: int = 7) -> Dict:
        """Get session analytics from DynamoDB"""
        try:
            if user_id:
                # Get sessions for specific user
                sessions = await self.session_repo.get_user_sessions(user_id, limit=100)
            else:
                # Get all recent sessions (would need different query in production)
                since_time = datetime.utcnow() - timedelta(days=days_back)
                response = self.session_repo.table.scan(
                    FilterExpression=Attr('created_at').gte(since_time.isoformat()) &
                                   Attr('SK').eq('METADATA')
                )
                sessions = [self.session_repo._item_to_session_summary(item) 
                          for item in response['Items']]
            
            # Analyze sessions
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.processing_status == 'completed'])
            failed_sessions = len([s for s in sessions if s.processing_status == 'failed'])
            
            # Intent distribution
            intent_distribution = {}
            for session in sessions:
                intent = session.intent or 'unknown'
                intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            
            return {
                'period_days': days_back,
                'total_sessions': total_sessions,
                'completion_rate': completed_sessions / max(total_sessions, 1),
                'failure_rate': failed_sessions / max(total_sessions, 1),
                'intent_distribution': intent_distribution,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting session analytics: {e}")
            return {}
```

## API Endpoints with DynamoDB Integration

```python
# app/routers/agent.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, Dict, Any
from app.agent.core_agent import CourseAnalysisAgent
from app.models.schemas import AgentRequest, AgentResponse
from app.utils.monitoring import AgentPerformanceMonitor
from app.database.repositories import AgentSessionRepository
from app.database.dynamodb_client import dynamodb_client

router = APIRouter(prefix="/agent", tags=["agent"])

# Initialize components
agent = CourseAnalysisAgent(config)
session_repo = AgentSessionRepository(dynamodb_client)
performance_monitor = AgentPerformanceMonitor(session_repo)

@router.post("/analyze", response_model=AgentResponse)
async def analyze_content(request: AgentRequest, background_tasks: BackgroundTasks):
    """Main agent endpoint with DynamoDB persistence"""
    try:
        response = await agent.process_request(
            user_request=request.request,
            session_id=request.session_id,
            context=request.context,
            user_id=request.user_id or "anonymous"
        )
        
        # Background task to clean up old sessions
        background_tasks.add_task(cleanup_expired_sessions)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session state and history from DynamoDB"""
    try:
        session = await session_repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session": session.dict(),
            "task_count": len(session.task_queue) + len(session.completed_tasks),
            "status": session.processing_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@router.get("/user/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 20):
    """Get user's recent sessions from DynamoDB"""
    try:
        sessions = await session_repo.get_user_sessions(user_id, limit)
        return {
            "user_id": user_id,
            "sessions": [session.dict() for session in sessions],
            "total": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user sessions: {str(e)}")

@router.get("/metrics/performance")
async def get_performance_metrics(hours_back: int = 24):
    """Get agent performance metrics"""
    try:
        metrics = await performance_monitor.get_performance_metrics(hours_back)
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/analytics/sessions")
async def get_session_analytics(user_id: Optional[str] = None, days_back: int = 7):
    """Get session analytics"""
    try:
        analytics = await performance_monitor.get_session_analytics(user_id, days_back)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

async def cleanup_expired_sessions():
    """Background task to clean up expired sessions"""
    # DynamoDB TTL will handle automatic cleanup, but we can do additional cleanup here
    try:
        # Could implement custom cleanup logic if needed
        print("Session cleanup completed")
    except Exception as e:
        print(f"Session cleanup failed: {e}")
```

## Local Development with DynamoDB Local

```python
# app/config.py
import os
from typing import Optional

class Config:
    # DynamoDB Configuration
    aws_region: str = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key_id: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')
    dynamodb_endpoint_url: Optional[str] = os.getenv('DYNAMODB_ENDPOINT_URL')  # For local development
    
    # Table Names
    sessions_table_name: str = os.getenv('DYNAMODB_SESSIONS_TABLE', 'ai-course-agent-sessions')
    content_cache_table_name: str = os.getenv('DYNAMODB_CONTENT_CACHE_TABLE', 'ai-course-agent-content-cache')
    
    # Agent Configuration
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    max_concurrent_tools: int = int(os.getenv('MAX_CONCURRENT_TOOLS', '3'))
    tool_execution_timeout: int = int(os.getenv('TOOL_EXECUTION_TIMEOUT', '300'))
    enable_content_caching: bool = os.getenv('ENABLE_CONTENT_CACHING', 'true').lower() == 'true'
    
    @property
    def is_local_development(self) -> bool:
        return bool(self.dynamodb_endpoint_url)

config = Config()
```

```bash
# docker-compose.yml for local development
version: '3.8'
services:
  dynamodb-local:
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal

  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
      - AWS_ACCESS_KEY_ID=local
      - AWS_SECRET_ACCESS_KEY=local
      - AWS_REGION=us-east-1
    depends_on:
      - dynamodb-local
```

This comprehensive DynamoDB integration provides:

1. **Scalable Data Architecture**: Single-table design with efficient access patterns
2. **Automatic TTL Management**: Sessions and cache expire automatically
3. **Performance Monitoring**: Built-in analytics using DynamoDB queries
4. **Concurrent Processing**: Optimized for high-throughput agent operations
5. **Caching Strategy**: Intelligent content caching to reduce API costs
6. **Local Development**: Full local development environment with DynamoDB Local

The implementation maintains all the autonomous agent capabilities while providing enterprise-grade persistence and scalability through DynamoDB.