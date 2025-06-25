from ..tools.base_tool import tool_registry, BaseTool
from ..utils.ai_client import AIClient
from ..models.agent_models import AgentResponse, ToolCall
from typing import List, Dict, Any

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> BaseTool:
        return self.tools.get(tool_name)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [tool.model_json_schema() for tool in self.tools.values()]

tool_registry = ToolRegistry()

class CourseAgent:
    def __init__(self, client: AIClient, tools: List[BaseTool] = None):
        self.client = client
        self.tools = {tool.name: tool for tool in tools} if tools else {}

    def add_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [tool.model_json_schema() for tool in self.tools.values()]

    async def generate_response(self, conversation: List[Dict[str, str]]) -> AgentResponse:
        pass