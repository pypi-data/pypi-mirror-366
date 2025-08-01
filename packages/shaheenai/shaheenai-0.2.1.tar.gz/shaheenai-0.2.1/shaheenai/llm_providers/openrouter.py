"""
OpenRouter provider implementation for ShaheenAI
===============================================

This module implements the OpenRouter provider for text generation using
the OpenRouter API, which provides access to multiple LLM models through
an OpenAI-compatible interface.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter provider implementation using OpenAI-compatible API.
    
    Supports:
    - Multiple models through OpenRouter (GPT, Claude, Llama, Gemini, etc.)
    - Both sync and async operations
    - Streaming responses
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenRouter provider.
        
        Args:
            config: Configuration dictionary containing:
                   - model: Model name (e.g., "openai/gpt-4", "anthropic/claude-3-haiku")
                   - api_key: OpenRouter API key
                   - base_url: OpenRouter base URL (defaults to OpenRouter API)
                   - Additional parameters
        """
        self.config = config
        self.model = config.get("model", "openai/gpt-3.5-turbo")
        self.api_key = config.get("api_key") or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = config.get("base_url", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY or OPENAI_API_KEY "
                "environment variable or pass api_key in config."
            )
        
        self._client = None
        self._async_client = None
        
        logger.info(f"OpenRouter provider initialized with model: {self.model}")
    
    def _get_client(self):
        """Get or create sync OpenAI client configured for OpenRouter."""
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
        """Get or create async OpenAI client configured for OpenRouter."""
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
        Generate a response using OpenRouter's API.
        
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
            logger.error(f"OpenRouter API error: {e}")
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
            logger.error(f"OpenRouter API error: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def stream_generate(self, messages: List[Dict[str, str]], **kwargs):
        """
        Generate streaming response using OpenRouter's API.
        
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
            logger.error(f"OpenRouter streaming API error: {e}")
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
            logger.error(f"OpenRouter async streaming API error: {e}")
            raise RuntimeError(f"Failed to generate async streaming response: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from OpenRouter.
        
        Returns:
            List of available model names
        """
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.base_url}/models", headers=headers)
            if response.status_code == 200:
                models_data = response.json()
                return [model["id"] for model in models_data.get("data", [])]
            else:
                logger.warning(f"Failed to fetch models from OpenRouter: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
        
        # Default fallback models available on OpenRouter
        return [
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "google/gemini-pro",
            "meta-llama/llama-2-70b-chat",
            "mistralai/mistral-7b-instruct"
        ]
    
    def __repr__(self) -> str:
        return f"OpenRouterProvider(model='{self.model}', base_url='{self.base_url}')"
