"""Core AI agent for course management and content generation."""

import asyncio
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.models.schemas import AgentRequest, AgentResponse, AIProvider
from app.models.agent_models import AgentSession, AgentTask, UserIntent, TaskPlan
from app.tools.base_tool import tool_registry
from app.utils.ai_client import ai_client
from app.config import settings


class CourseManagementAgent:
    """Main AI agent for course management and content generation."""

    def __init__(self):
        self.tool_registry = tool_registry
        self.ai_client = ai_client
        self.config = settings

        # Register available tools
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        from app.tools.content_analyzer import ContentAnalyzerTool
        from app.tools.file_processor import FileProcessorTool
        from app.tools.content_generator import ContentGeneratorTool
        from app.tools.slide_analyzer import SlideAnalyzerTool

        # Register tools
        self.tool_registry.register_tool(ContentAnalyzerTool())
        self.tool_registry.register_tool(FileProcessorTool())
        self.tool_registry.register_tool(ContentGeneratorTool())
        self.tool_registry.register_tool(SlideAnalyzerTool())

    async def process_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default_user",
        preferred_provider: Optional[AIProvider] = None,
    ) -> AgentResponse:
        """Main entry point for processing user requests."""
        start_time = datetime.utcnow()
        context = context or {}

        try:
            # Phase 1: Create session and analyze intent
            session = await self._create_session(user_id, user_request, context)
            intent = await self._analyze_intent(
                user_request, context, preferred_provider
            )

            session.intent = intent.primary_intent
            session.available_tools = self.tool_registry.available_tools

            # Phase 2: Check cache for similar requests
            content_hash = self._generate_content_hash(user_request, context)
            cached_result = await self._check_cache(content_hash, intent.primary_intent)

            if cached_result and self.config.enable_content_caching:
                return self._create_response_from_cache(cached_result, session)

            # Phase 3: Plan task execution
            task_plan = await self._create_task_plan(
                intent, session, preferred_provider
            )
            session.task_queue = task_plan.tasks

            # Phase 4: Execute tasks
            execution_results = await self._execute_tasks(session, preferred_provider)

            # Phase 5: Generate response
            response = await self._generate_response(
                user_request, execution_results, session, preferred_provider
            )

            # Phase 6: Cache results if successful
            if response.success and self.config.enable_content_caching:
                await self._cache_results(
                    content_hash, intent.primary_intent, response.data
                )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            response.processing_time = processing_time
            response.session_id = session.session_id

            return response

        except Exception as e:
            error_response = await self._handle_error(str(e), user_request)
            error_response.processing_time = (
                datetime.utcnow() - start_time
            ).total_seconds()
            return error_response

    async def _create_session(
        self, user_id: str, user_request: str, context: Dict[str, Any]
    ) -> AgentSession:
        """Create a new agent session."""
        return AgentSession(
            user_id=user_id,
            user_query=user_request,
            context=context,
            processing_status="planning",
        )

    async def _analyze_intent(
        self,
        user_request: str,
        context: Dict[str, Any],
        preferred_provider: Optional[AIProvider] = None,
    ) -> UserIntent:
        """Analyze user intent and extract key information."""

        intent_prompt = f"""
Analyze the following user request and classify the intent. Also extract key entities and requirements.

User Request: {user_request}
Context: {json.dumps(context, indent=2)}

Classify the primary intent as one of:
- analyze_course: Analyzing course content, structure, or quality
- analyze_slides: Analyzing slide images to extract course information
- process_exam: Processing exam questions or assessments
- match_content: Matching course content with exams or requirements
- generate_content: Creating new educational content
- optimize_analysis: Improving or optimizing existing analysis

Provide your response in JSON format:
{{
    "primary_intent": "intent_name",
    "confidence": 0.95,
    "secondary_intents": ["other_possible_intents"],
    "extracted_entities": {{
        "files": ["file1.pdf", "file2.pptx"],
        "target_audience": "beginners",
        "subject_area": "computer science",
        "content_type": "course_material"
    }},
    "context_requirements": ["file_processing", "content_analysis"],
    "suggested_tools": ["file_processor", "content_analyzer"],
    "complexity_score": 0.7
}}
"""

        messages = [
            {
                "role": "system",
                "content": "You are an expert at understanding educational content requests and classifying user intents.",
            },
            {"role": "user", "content": intent_prompt},
        ]

        response = await self.ai_client.generate_response(
            messages=messages,
            provider=preferred_provider,
            temperature=0.3,
            max_tokens=500,
        )

        try:
            intent_data = json.loads(response["content"])
            return UserIntent(**intent_data)
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to default intent
            return UserIntent(
                primary_intent="analyze_course",
                confidence=0.5,
                complexity_score=0.5,
                suggested_tools=["content_analyzer"],
            )

    async def _create_task_plan(
        self,
        intent: UserIntent,
        session: AgentSession,
        preferred_provider: Optional[AIProvider] = None,
    ) -> TaskPlan:
        """Create a multi-step task execution plan."""

        planning_prompt = f"""
            Create a detailed execution plan for the following request:

            User Query: {session.user_query}
            Primary Intent: {intent.primary_intent}
            Available Tools: {', '.join(self.tool_registry.available_tools)}
            Context: {json.dumps(session.context, indent=2)}

            Create a step-by-step plan with specific tasks. Each task should:
            1. Have a clear description
            2. Specify which tool to use
            3. Define the parameters for the tool
            4. Identify any dependencies on other tasks

            Provide your response in JSON format:
            {{
                "description": "Overall plan description",
                "tasks": [
                    {{
                        "task_type": "file_processing",
                        "description": "Extract content from uploaded files",
                        "tool_name": "file_processor",
                        "parameters": {{
                            "file_path": "path/to/file.pdf",
                            "extraction_type": "full"
                        }},
                        "dependencies": [],
                        "priority": 1
                    }},
                    {{
                        "task_type": "content_analysis",
                        "description": "Analyze extracted content",
                        "tool_name": "content_analyzer",
                        "parameters": {{
                            "content": "{{file_content}}",
                            "analysis_type": "comprehensive"
                        }},
                        "dependencies": ["task_1"],
                        "priority": 2
                    }}
                ],
                "estimated_duration": 30.0
            }}
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert task planner for educational content processing.",
            },
            {"role": "user", "content": planning_prompt},
        ]

        response = await self.ai_client.generate_response(
            messages=messages,
            provider=preferred_provider,
            temperature=0.3,
            max_tokens=1000,
        )

        try:
            plan_data = json.loads(response["content"])

            # Convert to AgentTask objects
            tasks = []
            for i, task_data in enumerate(plan_data.get("tasks", [])):
                task = AgentTask(
                    task_type=task_data.get("task_type", "unknown"),
                    description=task_data.get("description", ""),
                    tool_name=task_data.get("tool_name", ""),
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    priority=task_data.get("priority", i + 1),
                )
                tasks.append(task)

            return TaskPlan(
                session_id=session.session_id,
                intent=intent.primary_intent,
                description=plan_data.get("description", "Task execution plan"),
                tasks=tasks,
                estimated_duration=plan_data.get("estimated_duration"),
            )

        except (json.JSONDecodeError, Exception) as e:
            # Fallback to simple plan
            return self._create_fallback_plan(intent, session)

    def _create_fallback_plan(
        self, intent: UserIntent, session: AgentSession
    ) -> TaskPlan:
        """Create a simple fallback plan when AI planning fails."""
        tasks = []

        # Check if files need processing
        if "files" in session.context and session.context["files"]:
            for file_path in session.context["files"]:
                task = AgentTask(
                    task_type="file_processing",
                    description=f"Process file: {file_path}",
                    tool_name="file_processor",
                    parameters={"file_path": file_path, "extraction_type": "full"},
                    priority=1,
                )
                tasks.append(task)

        # Add content analysis task
        if intent.primary_intent in ["analyze_course", "generate_content"]:
            task = AgentTask(
                task_type="content_analysis",
                description="Analyze content",
                tool_name="content_analyzer",
                parameters={
                    "content": session.user_query,
                    "analysis_type": "comprehensive",
                },
                priority=2,
            )
            tasks.append(task)

        return TaskPlan(
            session_id=session.session_id,
            intent=intent.primary_intent,
            description="Fallback execution plan",
            tasks=tasks,
        )

    async def _execute_tasks(
        self, session: AgentSession, preferred_provider: Optional[AIProvider] = None
    ) -> List[Dict[str, Any]]:
        """Execute all tasks in the session."""
        results = []
        completed_task_ids = set()

        # Sort tasks by priority
        pending_tasks = sorted(session.task_queue, key=lambda t: t.priority)

        while pending_tasks:
            # Find tasks that can run (no unmet dependencies)
            ready_tasks = [
                task
                for task in pending_tasks
                if all(dep_id in completed_task_ids for dep_id in task.dependencies)
            ]

            if not ready_tasks:
                break  # No more tasks can run

            # Execute ready tasks (limit concurrency)
            batch_size = min(len(ready_tasks), self.config.max_concurrent_tools)
            current_batch = ready_tasks[:batch_size]

            # Execute tasks concurrently
            task_results = await asyncio.gather(
                *[self._execute_single_task(task, session) for task in current_batch],
                return_exceptions=True,
            )

            # Process results
            for i, result in enumerate(task_results):
                task = current_batch[i]

                if isinstance(result, Exception):
                    task.status = "failed"
                    task.error_message = str(result)
                else:
                    task.status = "completed"
                    task.result = (
                        result.data if result.success else {"error": result.error}
                    )
                    if result.success:
                        results.append(result.data)
                        completed_task_ids.add(task.task_id)

            # Remove completed/failed tasks
            pending_tasks = [t for t in pending_tasks if t not in current_batch]

        return results

    async def _execute_single_task(self, task: AgentTask, session: AgentSession):
        """Execute a single task."""
        tool = self.tool_registry.get_tool(task.tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {task.tool_name}")

        # Resolve parameter references (e.g., {{file_content}})
        resolved_params = await self._resolve_task_parameters(task.parameters, session)

        # Execute the tool
        return await tool._execute_with_timing(resolved_params)

    async def _resolve_task_parameters(
        self, parameters: Dict[str, Any], session: AgentSession
    ) -> Dict[str, Any]:
        """Resolve parameter references in task parameters."""
        resolved = {}

        for key, value in parameters.items():
            if (
                isinstance(value, str)
                and value.startswith("{{")
                and value.endswith("}}")
            ):
                # This is a reference to resolve
                ref_name = value[2:-2].strip()

                if ref_name == "user_query":
                    resolved[key] = session.user_query
                elif ref_name == "file_content":
                    # Get content from previous file processing tasks
                    file_content = self._get_file_content_from_session(session)
                    resolved[key] = file_content
                else:
                    resolved[key] = value  # Keep as-is if can't resolve
            else:
                resolved[key] = value

        return resolved

    def _get_file_content_from_session(self, session: AgentSession) -> str:
        """Extract file content from completed tasks."""
        for task in session.completed_tasks:
            if task.tool_name == "file_processor" and task.result:
                content = task.result.get("content", {})
                return content.get("text", "")
        return ""

    async def _generate_response(
        self,
        user_request: str,
        execution_results: List[Dict[str, Any]],
        session: AgentSession,
        preferred_provider: Optional[AIProvider] = None,
    ) -> AgentResponse:
        """Generate final response based on execution results."""

        response_prompt = f"""
            Generate a comprehensive response to the user's request based on the execution results.

            User Request: {user_request}
            Execution Results: {json.dumps(execution_results, indent=2)[:2000]}

            Provide a natural language response that:
            1. Directly addresses the user's request
            2. Summarizes key findings from the analysis
            3. Provides actionable insights or recommendations
            4. Suggests potential next steps

            Also provide structured data if applicable.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert educational consultant providing insights based on content analysis.",
            },
            {"role": "user", "content": response_prompt},
        ]

        try:
            response = await self.ai_client.generate_response(
                messages=messages,
                provider=preferred_provider,
                temperature=0.7,
                max_tokens=1500,
            )

            return AgentResponse(
                session_id=session.session_id,
                response=response["content"],
                data={"execution_results": execution_results},
                execution_summary=f"Executed {len(session.task_queue)} tasks successfully",
                agent_reasoning="Analyzed content and generated comprehensive response",
                suggested_follow_ups=[
                    "Generate additional content",
                    "Perform deeper analysis",
                ],
                success=True,
                cache_hit=False,
            )

        except Exception as e:
            return AgentResponse(
                session_id=session.session_id,
                response=f"I encountered an error while generating the response: {str(e)}",
                success=False,
                errors=[str(e)],
            )

    async def _check_cache(
        self, content_hash: str, intent: str
    ) -> Optional[Dict[str, Any]]:
        """Check if similar request has been cached."""
        # This would integrate with DynamoDB in a full implementation
        # For now, return None (no cache hit)
        return None

    async def _cache_results(
        self, content_hash: str, intent: str, data: Dict[str, Any]
    ):
        """Cache successful results."""
        # This would store results in DynamoDB in a full implementation
        pass

    def _generate_content_hash(self, user_request: str, context: Dict[str, Any]) -> str:
        """Generate hash for content caching."""
        content_to_hash = {"request": user_request, "context": context}
        content_str = json.dumps(content_to_hash, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _create_response_from_cache(
        self, cached_result: Dict[str, Any], session: AgentSession
    ) -> AgentResponse:
        """Create response from cached results."""
        return AgentResponse(
            session_id=session.session_id,
            response=cached_result.get("response", "Cached response"),
            data=cached_result.get("data"),
            success=True,
            cache_hit=True,
        )

    async def _handle_error(self, error: str, user_request: str) -> AgentResponse:
        """Handle errors gracefully."""
        return AgentResponse(
            session_id="error_session",
            response=f"I apologize, but I encountered an error while processing your request: {error}. Please try again or rephrase your request.",
            success=False,
            errors=[error],
        )


# Global agent instance
course_agent = CourseManagementAgent()
