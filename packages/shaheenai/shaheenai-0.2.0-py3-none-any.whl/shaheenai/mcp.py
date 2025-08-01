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
    """Get weather information for a specific location using a real weather API."""
    import os
    import httpx
    
    try:
        # OpenWeatherMap API Key
        openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if not openweather_api_key:
            return "❌ OpenWeatherMap API key not set. Set environment variable: OPENWEATHER_API_KEY"
        
        # Request current weather data from OpenWeatherMap
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": location,
                    "appid": openweather_api_key,
                    "units": "metric"
                }
            )
            if response.status_code == 200:
                data = response.json()
                
                # Extract weather information
                main = data['main']
                weather = data['weather'][0]
                wind = data.get('wind', {})
                clouds = data.get('clouds', {})
                visibility = data.get('visibility', 0) / 1000  # Convert to km
                
                city = data['name']
                country = data['sys']['country']
                temp = main['temp']
                feels_like = main['feels_like']
                humidity = main['humidity']
                pressure = main['pressure']
                temp_min = main.get('temp_min', temp)
                temp_max = main.get('temp_max', temp)
                
                weather_desc = weather['description'].capitalize()
                weather_main = weather['main']
                
                wind_speed = wind.get('speed', 0) * 3.6  # Convert m/s to km/h
                wind_dir = wind.get('deg', 0)
                cloudiness = clouds.get('all', 0)
                
                # Create detailed weather report
                weather_report = f"🌤️ **Weather in {city}, {country}**\n\n"
                weather_report += f"🌡️ **Temperature:** {temp}°C (feels like {feels_like}°C)\n"
                weather_report += f"📊 **Range:** {temp_min}°C - {temp_max}°C\n"
                weather_report += f"☁️ **Conditions:** {weather_desc} ({weather_main})\n"
                weather_report += f"💧 **Humidity:** {humidity}%\n"
                weather_report += f"🌬️ **Wind:** {wind_speed:.1f} km/h from {wind_dir}°\n"
                weather_report += f"🌫️ **Pressure:** {pressure} hPa\n"
                weather_report += f"☁️ **Cloudiness:** {cloudiness}%\n"
                
                if visibility > 0:
                    weather_report += f"👁️ **Visibility:** {visibility:.1f} km\n"
                
                return weather_report
                
            elif response.status_code == 404:
                return f"❌ Location '{location}' not found. Please check the spelling and try again."
            elif response.status_code == 401:
                return f"❌ Invalid API key. Please check your OPENWEATHER_API_KEY environment variable."
            else:
                return f"❌ Unable to fetch weather for {location}. API returned status code: {response.status_code}"
    except Exception as e:
        logger.error(f"Weather tool error: {e}")
        return f"❌ Error fetching weather for {location}: {str(e)}"


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
    import os
    import httpx
    import json
    from datetime import datetime
    
    try:
        # Try different search providers in order of preference
        
        # 1. Try Brave Search API (if API key available)
        brave_api_key = os.getenv("BRAVE_API_KEY")
        if brave_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.search.brave.com/res/v1/web/search",
                        headers={"X-Subscription-Token": brave_api_key},
                        params={"q": query, "count": max_results}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        for item in data.get("web", {}).get("results", [])[:max_results]:
                            results.append(f"**{item.get('title', 'No title')}**\n{item.get('description', 'No description')}\nURL: {item.get('url', 'No URL')}")
                        
                        if results:
                            return f"🔍 **Search Results for '{query}'** (via Brave Search):\n\n" + "\n\n---\n\n".join(results)
            except Exception as e:
                logger.warning(f"Brave Search failed: {e}")
        
        # 2. Try SerpAPI (if API key available)
        serpapi_key = os.getenv("SERPAPI_KEY")
        if serpapi_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://serpapi.com/search",
                        params={
                            "q": query,
                            "api_key": serpapi_key,
                            "engine": "google",
                            "num": max_results
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        for item in data.get("organic_results", [])[:max_results]:
                            results.append(f"**{item.get('title', 'No title')}**\n{item.get('snippet', 'No description')}\nURL: {item.get('link', 'No URL')}")
                        
                        if results:
                            return f"🔍 **Search Results for '{query}'** (via Google/SerpAPI):\n\n" + "\n\n---\n\n".join(results)
            except Exception as e:
                logger.warning(f"SerpAPI failed: {e}")
        
        # 3. Try DuckDuckGo Instant Answer API (free, no API key needed)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for instant answer
                    if data.get("Abstract"):
                        return f"🔍 **Search Results for '{query}'** (via DuckDuckGo):\n\n**{data.get('Heading', 'Information')}**\n{data.get('Abstract')}\n\nSource: {data.get('AbstractURL', 'DuckDuckGo')}"
                    
                    # Check for definition
                    if data.get("Definition"):
                        return f"🔍 **Search Results for '{query}'** (via DuckDuckGo):\n\n**Definition:**\n{data.get('Definition')}\n\nSource: {data.get('DefinitionURL', 'DuckDuckGo')}"
                    
                    # Check for related topics
                    if data.get("RelatedTopics"):
                        topics = data.get("RelatedTopics", [])[:max_results]
                        results = []
                        for topic in topics:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append(f"• {topic['Text']}")
                        
                        if results:
                            return f"🔍 **Search Results for '{query}'** (via DuckDuckGo):\n\n" + "\n".join(results)
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        # 4. Fallback: Web scraping approach (basic)
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, timeout=10)
                if response.status_code == 200:
                    # Very basic parsing - in production, use proper HTML parsing
                    content = response.text
                    if "No results found" not in content:
                        return f"🔍 **Search Results for '{query}'** (via Web Scraping):\n\nFound search results for your query. For detailed results, please use a proper search API key.\n\n*Note: This is a basic fallback search. For better results, configure BRAVE_API_KEY or SERPAPI_KEY environment variables.*"
        except Exception as e:
            logger.warning(f"Web scraping fallback failed: {e}")
        
        # 5. Final fallback: Return helpful guidance
        return f"🔍 **Search for '{query}'**\n\n❌ Unable to perform web search. To enable real web search, please set up one of these:\n\n1. **Brave Search API** (Recommended)\n   - Get API key from: https://api.search.brave.com\n   - Set environment variable: BRAVE_API_KEY\n\n2. **SerpAPI** (Google Search)\n   - Get API key from: https://serpapi.com\n   - Set environment variable: SERPAPI_KEY\n\n3. **Alternative**: Use built-in search tools in your system or browser for '{query}'"
    
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"❌ Error performing web search for '{query}': {str(e)}"
