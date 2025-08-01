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
    instructions: str = "You are a helpful AI assistant."
    llm: Union[str, Dict[str, Any]] = "openai/gpt-3.5-turbo"
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
        instructions: str = "You are a helpful AI assistant.",
        llm: Union[str, Dict[str, Any]] = "openai/gpt-3.5-turbo",
        tools: Optional[List[str]] = None,
        memory: bool = False,
        self_reflection: bool = False,
        max_iterations: int = 3,
        **kwargs
    ):
        """
        Initialize an Agent instance.
        
        Args:
            instructions: System instructions for the agent
            llm: LLM provider specification (string or dict config)
            tools: List of tool names to make available to the agent
            memory: Whether to enable conversation memory
            self_reflection: Whether to enable self-reflection capabilities
            max_iterations: Maximum number of reflection iterations
            **kwargs: Additional configuration options
        """
        self.config = AgentConfig(
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
        for tool_name in self.config.tools:
            try:
                # Tool loading logic would go here
                # For now, we'll create placeholder tools
                logger.info(f"Loading tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to load tool {tool_name}: {e}")
    
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
            # Add user message to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "user", "content": prompt})
            
            # Generate initial response
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
            # Add user message to conversation history
            if self.config.memory:
                self.conversation_history.append({"role": "user", "content": prompt})
            
            # Generate initial response
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
    
    async def _aapply_self_reflection(self, original_prompt: str, initial_response: str, **kwargs) -> str:
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
