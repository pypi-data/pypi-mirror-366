"""
Base classes for tool integration in ShaheenAI
==============================================

This module defines the base interfaces for tools that can be used
by agents in the ShaheenAI framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    default: Any = None


class BaseTool(ABC):
    """
    Base class for all tools in ShaheenAI.
    
    Tools are functions or methods that agents can invoke to perform
    specific tasks like web searches, calculations, API calls, etc.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the tool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """
        Get the list of parameters this tool accepts.
        
        Returns:
            List of ToolParameter objects describing the tool's parameters
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Result of the tool execution
        """
        pass
    
    @abstractmethod
    async def aexecute(self, **kwargs) -> Any:
        """
        Async version of execute method.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema in OpenAI function calling format.
        
        Returns:
            Dictionary containing the tool schema
        """
        parameters = self.get_parameters()
        
        properties = {}
        required = []
        
        for param in parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            
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
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def unregister(self, name: str):
        """Unregister a tool by name."""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return [tool.get_schema() for tool in self.tools.values()]


# Global tool registry
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry
