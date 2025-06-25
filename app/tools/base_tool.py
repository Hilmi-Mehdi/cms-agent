"""Base tool interface for the AI agent system."""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.models.schemas import ToolResult


class ToolParameter(BaseModel):
    """Model for tool parameter definitions."""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class ToolDefinition(BaseModel):
    """Model for tool function definitions."""
    name: str
    description: str
    parameters: List[ToolParameter]
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            
            if param.enum:
                properties[param.name]["enum"] = param.enum
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


class BaseTool(ABC):
    """Abstract base class for all agent tools."""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('tool', '')
        self.definition = self.get_definition()
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition for function calling."""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    async def _execute_with_timing(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute tool with automatic timing and error handling."""
        start_time = time.time()
        
        try:
            # Validate parameters
            self._validate_parameters(parameters)
            
            # Execute the tool
            result = await self.execute(parameters)
            
            # Add timing information
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.tool_name = self.name
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate tool parameters."""
        required_params = [p.name for p in self.definition.parameters if p.required]
        
        for param_name in required_params:
            if param_name not in parameters:
                raise ValueError(f"Missing required parameter: {param_name}")
        
        # Basic type validation
        for param in self.definition.parameters:
            if param.name in parameters:
                value = parameters[param.name]
                
                if param.type == "string" and not isinstance(value, str):
                    raise ValueError(f"Parameter {param.name} must be a string")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Parameter {param.name} must be a number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Parameter {param.name} must be a boolean")
                elif param.type == "array" and not isinstance(value, list):
                    raise ValueError(f"Parameter {param.name} must be an array")
                elif param.type == "object" and not isinstance(value, dict):
                    raise ValueError(f"Parameter {param.name} must be an object")
    
    def get_openai_function(self) -> Dict[str, Any]:
        """Get OpenAI function calling format."""
        return self.definition.to_openai_function()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions."""
        return [tool.definition for tool in self._tools.values()]
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format."""
        return [tool.get_openai_function() for tool in self._tools.values()]
    
    @property
    def available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tools.keys())
    
    def remove_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all tools from the registry."""
        self._tools.clear()


# Global tool registry instance
tool_registry = ToolRegistry() 