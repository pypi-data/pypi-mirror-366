"""
OpenAI provider implementation for ShaheenAI
============================================

This module implements the OpenAI provider for text generation using
the OpenAI API, supporting both sync and async operations.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider implementation using the OpenAI Python client.
    
    Supports:
    - GPT-3.5, GPT-4, and other OpenAI models
    - Custom base URLs for OpenAI-compatible endpoints (like Groq)
    - Both sync and async operations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dictionary containing:
                   - model: Model name (e.g., "gpt-3.5-turbo")
                   - api_key: OpenAI API key
                   - base_url: Optional custom base URL
                   - Additional parameters
        """
        self.config = config
        self.model = config.get("model", "gpt-3.5-turbo")
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.base_url = config.get("base_url") or os.getenv("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key in config."
            )
        
        self._client = None
        self._async_client = None
        
        logger.info(f"OpenAI provider initialized with model: {self.model}")
    
    def _get_client(self):
        """Get or create sync OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError(
                    "OpenAI library not found. Install with: pip install openai"
                )
        return self._client
    
    def _get_async_client(self):
        """Get or create async OpenAI client."""
        if self._async_client is None:
            try:
                import openai
                self._async_client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError(
                    "OpenAI library not found. Install with: pip install openai"
                )
        return self._async_client
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response using OpenAI's chat completions API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Returns:
            Generated response as a string
        """
        client = self._get_client()
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params and key not in ["temperature", "max_tokens"]:
                params[key] = value
        
        try:
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
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
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params and key not in ["temperature", "max_tokens"]:
                params[key] = value
        
        try:
            response = await client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def stream_generate(self, messages: List[Dict[str, str]], **kwargs):
        """
        Generate streaming response using OpenAI's chat completions API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Yields:
            Response chunks as they arrive
        """
        client = self._get_client()
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": True,
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params and key not in ["temperature", "max_tokens"]:
                params[key] = value
        
        try:
            stream = client.chat.completions.create(**params)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            raise RuntimeError(f"Failed to generate streaming response: {str(e)}")
    
    async def astream_generate(self, messages: List[Dict[str, str]], **kwargs):
        """
        Async version of stream_generate method.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters like temperature, max_tokens, etc.
        
        Yields:
            Response chunks as they arrive
        """
        client = self._get_async_client()
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": True,
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params and key not in ["temperature", "max_tokens"]:
                params[key] = value
        
        try:
            stream = await client.chat.completions.create(**params)
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI async streaming API error: {e}")
            raise RuntimeError(f"Failed to generate async streaming response: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from OpenAI API.
        
        Returns:
            List of available model names
        """
        client = self._get_client()
        
        try:
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to fetch models: {e}")
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]  # Default fallback
    
    def __repr__(self) -> str:
        return f"OpenAIProvider(model='{self.model}', base_url='{self.base_url}')"
