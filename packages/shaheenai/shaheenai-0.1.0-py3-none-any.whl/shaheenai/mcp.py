"""
MCP (Model Context Protocol) module for ShaheenAI
==================================================

This module provides the MCP server interface for tool integrations,
allowing agents to interact with external APIs and services through
a standardized protocol.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union
from functools import wraps
from pydantic import BaseModel
import inspect


logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of a tool that can be used by agents."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


class ToolRegistry:
    """Registry to manage tools available to agents."""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register(self, name: str, func: Callable, description: str = None):
        """Register a tool function."""
        if description is None:
            description = func.__doc__ or f"Tool: {name}"
        
        # Extract parameter information from function signature
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": "string",  # Default type
                "required": param.default == inspect.Parameter.empty
            }
            
            # Try to infer type from annotations
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_info["type"] = "string"
                elif param.annotation == int:
                    param_info["type"] = "integer"
                elif param.annotation == float:
                    param_info["type"] = "number"
                elif param.annotation == bool:
                    param_info["type"] = "boolean"
            
            parameters[param_name] = param_info
        
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            function=func
        )
        
        self.tools[name] = tool_def
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get tool definitions in a format suitable for LLM function calling."""
        definitions = {}
        for name, tool in self.tools.items():
            definitions[name] = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": [
                        param_name for param_name, param_info in tool.parameters.items()
                        if param_info.get("required", False)
                    ]
                }
            }
        return definitions


# Global tool registry
_tool_registry = ToolRegistry()


def tool(name: str = None, description: str = None):
    """
    Decorator to register a function as a tool.
    
    Args:
        name: Name of the tool (defaults to function name)
        description: Description of what the tool does
    
    Example:
        @tool()
        async def get_weather(location: str) -> str:
            \"\"\"Get weather information for a location.\"\"\"
            return "Sunny, 25°C"
    """
    def decorator(func: Callable):
        tool_name = name or func.__name__
        _tool_registry.register(tool_name, func, description)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class MCP:
    """
    MCP (Model Context Protocol) server for managing tool integrations.
    
    This class provides a lightweight server interface that can register
    async tools and expose them to agents via the MCP protocol.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize MCP server.
        
        Args:
            host: Host address to bind the server
            port: Port number to bind the server
        """
        self.host = host
        self.port = port
        self.registry = _tool_registry
        self._server = None
        logger.info(f"MCP server initialized on {host}:{port}")
    
    def tool(self, name: str = None, description: str = None):
        """
        Decorator method to register tools with this MCP instance.
        
        Args:
            name: Name of the tool (defaults to function name)
            description: Description of what the tool does
        """
        return tool(name, description)
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a registered tool by name.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result from the tool function
        """
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            if asyncio.iscoroutinefunction(tool_def.function):
                result = await tool_def.function(**kwargs)
            else:
                result = tool_def.function(**kwargs)
            
            logger.info(f"Tool '{tool_name}' executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            raise
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tool definitions."""
        return self.registry.get_tool_definitions()
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return self.registry.list_tools()
    
    async def start_server(self):
        """Start the MCP server (async version)."""
        try:
            # This would start an actual server in a full implementation
            # For now, we'll just log that the server is starting
            logger.info(f"MCP server starting on {self.host}:{self.port}")
            logger.info(f"Available tools: {', '.join(self.list_tools())}")
            
            # In a real implementation, this would start a FastAPI or similar server
            # that listens for MCP protocol messages and routes them to tool calls
            
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            raise
    
    def run(self):
        """Run the MCP server (sync version)."""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("MCP server stopped by user")
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
    
    def register_tool(self, name: str, func: Callable, description: str = None):
        """
        Manually register a tool function.
        
        Args:
            name: Name of the tool
            func: Function to register as a tool
            description: Description of what the tool does
        """
        self.registry.register(name, func, description)
    
    def unregister_tool(self, name: str):
        """
        Unregister a tool by name.
        
        Args:
            name: Name of the tool to unregister
        """
        if name in self.registry.tools:
            del self.registry.tools[name]
            logger.info(f"Unregistered tool: {name}")
        else:
            logger.warning(f"Tool '{name}' not found for unregistration")
    
    def __repr__(self) -> str:
        return f"MCP(host='{self.host}', port={self.port}, tools={len(self.list_tools())})"


# Convenience functions for global tool registry
def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _tool_registry


def list_available_tools() -> List[str]:
    """List all available tools in the global registry."""
    return _tool_registry.list_tools()


def get_tool_definitions() -> Dict[str, Dict[str, Any]]:
    """Get all tool definitions from the global registry."""
    return _tool_registry.get_tool_definitions()


# Example tools for demonstration
@tool(description="Get current weather for a location")
async def get_weather(location: str) -> str:
    """Get weather information for a specific location."""
    # This would normally call a real weather API
    return f"Weather in {location}: Sunny, 25°C"


@tool(description="Calculate the result of a mathematical expression")
def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely."""
    try:
        # Basic calculator - in production, use a more secure evaluation method
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool(description="Search the internet for information")
async def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet for information about a query."""
    # This would normally integrate with a real search API
    return f"Search results for '{query}': [Mock results - integrate with real search API]"
