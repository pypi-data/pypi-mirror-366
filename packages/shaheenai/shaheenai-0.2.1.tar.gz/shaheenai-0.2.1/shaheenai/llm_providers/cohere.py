"""
Cohere provider implementation for ShaheenAI
============================================

This module implements the Cohere provider for text generation using
the Cohere API, supporting both sync and async operations.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class CohereProvider(BaseLLMProvider):
    """
    Cohere provider implementation using the Cohere Python client.
    
    Supports:
    - Command, Command-Light, and other Cohere models
    - Both sync and async operations
    - Streaming responses
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Cohere provider.
        
        Args:
            config: Configuration dictionary containing:
                   - model: Model name (e.g., "command", "command-light")
                   - api_key: Cohere API key
                   - Additional parameters
        """
        self.config = config
        self.model = config.get("model", "command")
        self.api_key = config.get("api_key") or os.getenv("COHERE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Cohere API key is required. Set COHERE_API_KEY environment variable "
                "or pass api_key in config."
            )
        
        self._client = None
        self._async_client = None
        
        logger.info(f"Cohere provider initialized with model: {self.model}")
    
    def _get_client(self):
        """Get or create sync Cohere client."""
        if self._client is None:
            try:
                import cohere
                self._client = cohere.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Cohere library not found. Install with: pip install cohere"
                )
        return self._client
    
    def _get_async_client(self):
        """Get or create async Cohere client."""
        if self._async_client is None:
            try:
                import cohere
                self._async_client = cohere.AsyncClient(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Cohere library not found. Install with: pip install cohere"
                )
        return self._async_client
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to a single prompt string for Cohere.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Single prompt string
        """
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Cohere's generate API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Returns:
            Generated response as a string
        """
        client = self._get_client()
        prompt = self._messages_to_prompt(messages)
        
        # Prepare parameters
        params = {
            "model": self.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add any additional Cohere-specific parameters
        cohere_params = ["k", "p", "frequency_penalty", "presence_penalty", "stop_sequences"]
        for param in cohere_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        try:
            response = client.generate(**params)
            return response.generations[0].text.strip()
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Async version of generate method.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Returns:
            Generated response as a string
        """
        client = self._get_async_client()
        prompt = self._messages_to_prompt(messages)
        
        # Prepare parameters
        params = {
            "model": self.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add any additional Cohere-specific parameters
        cohere_params = ["k", "p", "frequency_penalty", "presence_penalty", "stop_sequences"]
        for param in cohere_params:
            if param in kwargs:
                params[param] = kwargs[param]
        
        try:
            response = await client.generate(**params)
            return response.generations[0].text.strip()
            
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def chat_generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using Cohere's chat API (if available).
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            Generated response as a string
        """
        client = self._get_client()
        
        # Convert messages to Cohere chat format
        chat_history = []
        current_message = None
        
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            
            if role == "system":
                # System messages can be handled as preamble in some cases
                continue
            elif role == "user":
                current_message = content
            elif role == "assistant":
                if current_message:
                    chat_history.append({
                        "user_name": "User",
                        "text": current_message
                    })
                    chat_history.append({
                        "user_name": "Chatbot", 
                        "text": content
                    })
                    current_message = None
        
        # If there's a remaining user message, that's our current query
        if current_message is None and messages:
            current_message = messages[-1].get("content", "")
        
        params = {
            "model": self.model,
            "message": current_message,
            "chat_history": chat_history,
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        try:
            response = client.chat(**params)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"Cohere chat API error, falling back to generate: {e}")
            # Fallback to generate API
            return self.generate(messages, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available Cohere models.
        
        Returns:
            List of available model names
        """
        # Cohere doesn't have a public models endpoint, so return known models
        return [
            "command",
            "command-light",
            "command-nightly",
            "command-light-nightly"
        ]
    
    def __repr__(self) -> str:
        return f"CohereProvider(model='{self.model}')"
