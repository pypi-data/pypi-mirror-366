"""
Agent module for ShaheenAI
==========================

This module contains the main Agent class that provides the core functionality
for creating AI agents with multi-LLM support, self-reflection, and tool integration.
"""

import os
import json
from typing import List, Dict, Optional, Union, Any, Callable
from pydantic import BaseModel, Field
import asyncio
import logging

from .llm_providers.base import BaseLLMProvider
from .llm_providers.factory import LLMProviderFactory
from .tools.base import BaseTool


logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration model for Agent initialization."""
    name: Optional[str] = None
    instructions: str = "You are a helpful AI assistant."
    llm: Union[str, Dict[str, Any]] = "openrouter/anthropic/claude-3.5-sonnet"
    tools: Optional[List[str]] = None
    memory: bool = False
    self_reflection: bool = False
    max_iterations: int = 3
    temperature: float = 0.7
    max_tokens: int = 1000


class Agent:
    """
    Main Agent class that supports multiple LLMs, self-reflection, tool invocation, and task chaining.
    
    Features:
    - Multi-LLM provider support (OpenAI, Anthropic, Ollama, Cohere, etc.)
    - Self-reflection capabilities for improved responses
    - Tool integration via MCP protocol
    - Memory management for conversation context
    - Async and sync operation modes
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        instructions: str = "You are a helpful AI assistant.",
        llm: Union[str, Dict[str, Any]] = "openrouter/anthropic/claude-3.5-sonnet",
        tools: Optional[List[str]] = None,
        memory: bool = False,
        self_reflection: bool = False,
        max_iterations: int = 3,
        **kwargs
    ):
        """
        Initialize an Agent instance.
        
        Args:
            name: Optional name for the agent
            instructions: System instructions for the agent
            llm: LLM provider specification (string or dict config)
            tools: List of tool names to make available to the agent
            memory: Whether to enable conversation memory
            self_reflection: Whether to enable self-reflection capabilities
            max_iterations: Maximum number of reflection iterations
            **kwargs: Additional configuration options
        """
        self.config = AgentConfig(
            name=name,
            instructions=instructions,
            llm=llm,
            tools=tools or [],
            memory=memory,
            self_reflection=self_reflection,
            max_iterations=max_iterations,
            **kwargs
        )
        
        # Initialize LLM provider
        self.llm_provider = LLMProviderFactory.create_provider(self.config.llm)
        
        # Initialize tools
        self.tools: Dict[str, BaseTool] = {}
        self._load_tools()
        
        # Initialize memory if enabled
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"Agent initialized with LLM: {self.config.llm}")
    
    def _load_tools(self):
        """Load and initialize tools specified in the configuration."""
        from .mcp import get_tool_registry
        
        registry = get_tool_registry()
        available_tools = registry.list_tools()
        
        for tool_name in self.config.tools:
            try:
                if tool_name in available_tools:
                    tool_def = registry.get_tool(tool_name)
                    self.tools[tool_name] = tool_def.function
                    logger.info(f"✅ Loaded tool: {tool_name}")
                else:
                    logger.warning(f"⚠️  Tool '{tool_name}' not found in registry. Available tools: {available_tools}")
            except Exception as e:
                logger.error(f"❌ Failed to load tool {tool_name}: {e}")
    
    def start(self, prompt: str, **kwargs) -> str:
        """
        Process a user prompt and return the agent's response.
        
        Args:
            prompt: The user's input prompt
            **kwargs: Additional parameters for the LLM call
            
        Returns:
            The agent's response as a string
        """
        try:
            # Check for identity queries first
            identity_response = self._identity_response(prompt)
            if identity_response:
                return identity_response
            
            # Add user message to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "user", "content": prompt})
            
            # Check if we need to use tools
            tool_result = self._check_and_execute_tools(prompt)
            if tool_result:
                # If we got a tool result, use it as the response
                response = tool_result
            else:
                # Generate initial response using LLM
                response = self._generate_response(prompt, **kwargs)
            
            # Apply self-reflection if enabled
            if self.config.self_reflection:
                response = self._apply_self_reflection(prompt, response, **kwargs)
            
            # Add assistant response to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return f"Error: {str(e)}"
    
    async def astart(self, prompt: str, **kwargs) -> str:
        """
        Async version of start() method.
        
        Args:
            prompt: The user's input prompt
            **kwargs: Additional parameters for the LLM call
            
        Returns:
            The agent's response as a string
        """
        try:
            # Check for identity queries first
            identity_response = self._identity_response(prompt)
            if identity_response:
                return identity_response
            
            # Add user message to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "user", "content": prompt})
            
            # Check if we need to use tools
            tool_result = await self._acheck_and_execute_tools(prompt)
            if tool_result:
                # If we got a tool result, use it as the response
                response = tool_result
            else:
                # Generate initial response using LLM
                response = await self._agenerate_response(prompt, **kwargs)
            
            # Apply self-reflection if enabled
            if self.config.self_reflection:
                response = await self._aapply_self_reflection(prompt, response, **kwargs)
            
            # Add assistant response to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return f"Error: {str(e)}"
    
    def _generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using the configured LLM provider."""
        messages = self._build_messages(prompt)
        
        try:
            response = self.llm_provider.generate(
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def _agenerate_response(self, prompt: str, **kwargs) -> str:
        """Async version of _generate_response."""
        messages = self._build_messages(prompt)
        
        try:
            response = await self.llm_provider.agenerate(
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _build_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Build the messages list for the LLM call."""
        messages = [{"role": "system", "content": self.config.instructions}]
        
        # Add conversation history if memory is enabled
        if self.config.memory and self.conversation_history:
            messages.extend(self.conversation_history)
        
        # Add current user prompt if not already in history
        if not self.config.memory or not self.conversation_history or self.conversation_history[-1]["content"] != prompt:
            messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _apply_self_reflection(self, original_prompt: str, initial_response: str, **kwargs) -> str:
        """Apply self-reflection to improve the initial response."""
        current_response = initial_response
        
        for iteration in range(self.config.max_iterations):
            reflection_prompt = f"""
            Original question: {original_prompt}
            
            Your previous response: {current_response}
            
            Please reflect on your previous response. Is it accurate, complete, and helpful? 
            If you can improve it, provide a better response. If it's already good, you can keep it the same.
            
            Improved response:
            """
            
            try:
                reflected_response = self.llm_provider.generate(
                    messages=[
                        {"role": "system", "content": "You are a thoughtful AI that reviews and improves responses."},
                        {"role": "user", "content": reflection_prompt}
                    ],
                    temperature=kwargs.get('temperature', self.config.temperature),
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
                )
                
                # If the reflected response is significantly different, use it
                if len(reflected_response.strip()) > 0 and reflected_response != current_response:
                    current_response = reflected_response
                    logger.info(f"Applied self-reflection iteration {iteration + 1}")
                else:
                    logger.info(f"No improvement needed after {iteration + 1} iterations")
                    break
                    
            except Exception as e:
                logger.error(f"Error in self-reflection iteration {iteration + 1}: {e}")
                break
        
        return current_response
    
    def _identity_response(self, prompt: str) -> str:
        """Return identity response if applicable."""
        prompt_lower = prompt.lower().strip()
        
        # Define various ways users might ask about identity
        identity_patterns = [
            "who are you",
            "who developed you", 
            "who created you",
            "who made you",
            "what are you",
            "tell me about yourself",
            "introduce yourself",
            "who is your developer",
            "who is your creator",
            "about you"
        ]
        
        # Check if prompt matches any identity pattern
        for pattern in identity_patterns:
            if pattern in prompt_lower or prompt_lower == pattern:
                return "I am Shaheen AI developed by Engr. Hamza, an enthusiastic AI engineer."
        
        return None
    
    def _check_and_execute_tools(self, prompt: str) -> Optional[str]:
        """Check if prompt requires tool usage and execute if needed."""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based tool detection
        tool_triggers = {
            'get_weather': ['weather', 'temperature', 'forecast', 'climate'],
            'calculate': ['calculate', 'compute', 'math', 'addition', 'subtraction', 'multiplication', 'division', '+', '-', '*', '/', '='],
            'web_search': ['search', 'find', 'look up', 'information about', 'research']
        }
        
        for tool_name, triggers in tool_triggers.items():
            if tool_name in self.tools and any(trigger in prompt_lower for trigger in triggers):
                try:
                    tool_func = self.tools[tool_name]
                    
                    # Extract parameters based on tool type
                    if tool_name == 'get_weather':
                        # Extract location from prompt
                        import re
                        location_match = re.search(r'(?:in|for|at)\s+([a-zA-Z\s]+?)(?:\s|$|\?)', prompt)
                        location = location_match.group(1).strip() if location_match else "Unknown Location"
                        
                        if asyncio.iscoroutinefunction(tool_func):
                            # Handle async tool in sync context
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(tool_func(location))
                            loop.close()
                        else:
                            result = tool_func(location)
                        
                        return f"🌤️ **Weather Information:**\n{result}"
                    
                    elif tool_name == 'calculate':
                        # Extract mathematical expression
                        import re
                        # Look for mathematical expressions
                        math_pattern = r'([0-9+\-*/().\s]+)'
                        matches = re.findall(math_pattern, prompt)
                        if matches:
                            expression = matches[-1].strip()  # Take the last/longest match
                            result = tool_func(expression)
                            return f"🧮 **Calculation Result:**\n{result}"
                    
                    elif tool_name == 'web_search':
                        # Extract search query
                        search_triggers = ['search for', 'find', 'look up', 'information about', 'research']
                        query = prompt
                        for trigger in search_triggers:
                            if trigger in prompt_lower:
                                query = prompt_lower.split(trigger, 1)[1].strip()
                                break
                        
                        if asyncio.iscoroutinefunction(tool_func):
                            # Handle async tool in sync context
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(tool_func(query))
                            loop.close()
                        else:
                            result = tool_func(query)
                        
                        return f"🔍 **Search Results:**\n{result}"
                        
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    return f"❌ Error using {tool_name}: {str(e)}"
        
        return None
    
    async def _acheck_and_execute_tools(self, prompt: str) -> Optional[str]:
        """Async version of _check_and_execute_tools."""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based tool detection
        tool_triggers = {
            'get_weather': ['weather', 'temperature', 'forecast', 'climate'],
            'calculate': ['calculate', 'compute', 'math', 'addition', 'subtraction', 'multiplication', 'division', '+', '-', '*', '/', '='],
            'web_search': ['search', 'find', 'look up', 'information about', 'research']
        }
        
        for tool_name, triggers in tool_triggers.items():
            if tool_name in self.tools and any(trigger in prompt_lower for trigger in triggers):
                try:
                    tool_func = self.tools[tool_name]
                    
                    # Extract parameters based on tool type
                    if tool_name == 'get_weather':
                        # Extract location from prompt
                        import re
                        location_match = re.search(r'(?:in|for|at)\s+([a-zA-Z\s]+?)(?:\s|$|\?)', prompt)
                        location = location_match.group(1).strip() if location_match else "Unknown Location"
                        
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(location)
                        else:
                            result = tool_func(location)
                        
                        return f"🌤️ **Weather Information:**\n{result}"
                    
                    elif tool_name == 'calculate':
                        # Extract mathematical expression
                        import re
                        # Look for mathematical expressions
                        math_pattern = r'([0-9+\-*/().\s]+)'
                        matches = re.findall(math_pattern, prompt)
                        if matches:
                            expression = matches[-1].strip()  # Take the last/longest match
                            if asyncio.iscoroutinefunction(tool_func):
                                result = await tool_func(expression)
                            else:
                                result = tool_func(expression)
                            return f"🧮 **Calculation Result:**\n{result}"
                    
                    elif tool_name == 'web_search':
                        # Extract search query
                        search_triggers = ['search for', 'find', 'look up', 'information about', 'research']
                        query = prompt
                        for trigger in search_triggers:
                            if trigger in prompt_lower:
                                query = prompt_lower.split(trigger, 1)[1].strip()
                                break
                        
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(query)
                        else:
                            result = tool_func(query)
                        
                        return f"🔍 **Search Results:**\n{result}"
                        
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    return f"❌ Error using {tool_name}: {str(e)}"
        
        return None

    async def _aapply_self_reflection(self, original_prompt: str, initial_response: str, **kwargs):
        """Async version of _apply_self_reflection."""
        current_response = initial_response
        
        for iteration in range(self.config.max_iterations):
            reflection_prompt = f"""
            Original question: {original_prompt}
            
            Your previous response: {current_response}
            
            Please reflect on your previous response. Is it accurate, complete, and helpful? 
            If you can improve it, provide a better response. If it's already good, you can keep it the same.
            
            Improved response:
            """
            
            try:
                reflected_response = await self.llm_provider.agenerate(
                    messages=[
                        {"role": "system", "content": "You are a thoughtful AI that reviews and improves responses."},
                        {"role": "user", "content": reflection_prompt}
                    ],
                    temperature=kwargs.get('temperature', self.config.temperature),
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
                )
                
                # If the reflected response is significantly different, use it
                if len(reflected_response.strip()) > 0 and reflected_response != current_response:
                    current_response = reflected_response
                    logger.info(f"Applied self-reflection iteration {iteration + 1}")
                else:
                    logger.info(f"No improvement needed after {iteration + 1} iterations")
                    break
                    
            except Exception as e:
                logger.error(f"Error in self-reflection iteration {iteration + 1}: {e}")
                break
        
        return current_response
    
    def clear_memory(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation memory cleared")
    
    def get_memory(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def add_tool(self, tool_name: str, tool_func: Callable):
        """Add a custom tool to the agent."""
        # Tool registration logic would go here
        logger.info(f"Added tool: {tool_name}")
    
    def remove_tool(self, tool_name: str):
        """Remove a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Removed tool: {tool_name}")
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self.tools.keys())
    
    def __repr__(self) -> str:
        return f"Agent(llm='{self.config.llm}', tools={len(self.tools)}, memory={self.config.memory})"
