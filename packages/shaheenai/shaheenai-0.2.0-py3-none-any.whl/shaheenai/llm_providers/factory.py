"""
LLM Provider Factory for ShaheenAI
==================================

This module contains the factory implementation for creating LLM provider
instances based on configuration strings or dictionaries.
"""

import os
import logging
from typing import Union, Dict, Any
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory class to create LLM provider instances based on configuration.
    
    Supports various provider formats:
    - Simple string: "openai", "cohere", "ollama"
    - Provider/model format: "openai/gpt-4", "groq/llama-3.1-8b-instant"
    - Dictionary configuration with full parameters
    """
    
    @staticmethod
    def create_provider(config: Union[str, Dict[str, Any]]) -> BaseLLMProvider:
        """
        Create a provider instance based on the given configuration.
        
        Args:
            config: Provider configuration - can be:
                   - String: "openai", "groq/llama-3.1-8b-instant"
                   - Dict: {"model": "gpt-4", "provider": "openai", ...}
        
        Returns:
            An instance of a subclass of BaseLLMProvider
        
        Raises:
            ValueError: If the provider is not supported
            ImportError: If required dependencies are not installed
        """
        if isinstance(config, str):
            provider_info = LLMProviderFactory._parse_provider_string(config)
        elif isinstance(config, dict):
            provider_info = LLMProviderFactory._parse_provider_dict(config)
        else:
            raise ValueError(f"Invalid config type: {type(config)}. Expected str or dict.")
        
        provider_name = provider_info["provider"].lower()
        
        try:
            if provider_name in ["openai", "gpt"]:
                from .openai import OpenAIProvider
                return OpenAIProvider(provider_info)
            
            elif provider_name in ["anthropic", "claude"]:
                from .anthropic import AnthropicProvider
                return AnthropicProvider(provider_info)
            
            elif provider_name == "cohere":
                from .cohere import CohereProvider
                return CohereProvider(provider_info)
            
            elif provider_name == "groq":
                from .groq import GroqProvider
                return GroqProvider(provider_info)
            
            elif provider_name == "ollama":
                from .ollama import OllamaProvider
                return OllamaProvider(provider_info)
            
            elif provider_name in ["gemini", "google"]:
                from .google import GoogleProvider
                return GoogleProvider(provider_info)
            
            elif provider_name in ["openrouter", "or"]:
                from .openrouter import OpenRouterProvider
                return OpenRouterProvider(provider_info)
            
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
                
        except ImportError as e:
            logger.error(f"Failed to import provider {provider_name}: {e}")
            raise ImportError(
                f"Provider '{provider_name}' requires additional dependencies. "
                f"Install with: pip install shaheenai[{provider_name}]"
            )
    
    @staticmethod
    def _parse_provider_string(config_str: str) -> Dict[str, Any]:
        """
        Parse a provider configuration string.
        
        Examples:
        - "openai" -> {"provider": "openai", "model": "gpt-3.5-turbo"}
        - "groq/llama-3.1-8b-instant" -> {"provider": "groq", "model": "llama-3.1-8b-instant"}
        """
        if "/" in config_str:
            provider, model = config_str.split("/", 1)
        else:
            provider = config_str
            model = LLMProviderFactory._get_default_model(provider)
        
        return {
            "provider": provider,
            "model": model,
            "api_key": LLMProviderFactory._get_api_key(provider),
            "base_url": LLMProviderFactory._get_base_url(provider),
        }
    
    @staticmethod
    def _parse_provider_dict(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a provider configuration dictionary.
        
        Example:
        {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "sk-...",
            "temperature": 0.7
        }
        """
        provider = config_dict.get("provider") or config_dict.get("model", "").split("/")[0]
        if not provider:
            raise ValueError("Provider configuration must specify 'provider' or 'model'")
        
        result = {
            "provider": provider,
            "model": config_dict.get("model", LLMProviderFactory._get_default_model(provider)),
            "api_key": config_dict.get("api_key") or LLMProviderFactory._get_api_key(provider),
            "base_url": config_dict.get("base_url") or LLMProviderFactory._get_base_url(provider),
        }
        
        # Copy additional parameters
        for key, value in config_dict.items():
            if key not in result:
                result[key] = value
        
        return result
    
    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get the default model for a provider."""
        defaults = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-haiku-20240307",
            "cohere": "command",
            "groq": "llama-3.1-8b-instant",
            "ollama": "llama2",
            "google": "gemini-1.5-flash",
            "gemini": "gemini-1.5-flash",
        }
        return defaults.get(provider.lower(), "default")
    
    @staticmethod
    def _get_api_key(provider: str) -> str:
        """Get API key from environment variables."""
        env_vars = {
            "openai": ["OPENAI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
            "cohere": ["COHERE_API_KEY"],
            "groq": ["GROQ_API_KEY"],
            "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"],
            "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"],
            "openrouter": ["OPENROUTER_API_KEY", "OPENAI_API_KEY"],
        }
        
        for env_var in env_vars.get(provider.lower(), []):
            api_key = os.getenv(env_var)
            if api_key:
                return api_key
        
        return None
    
    @staticmethod
    def _get_base_url(provider: str) -> str:
        """Get base URL for provider from environment variables."""
        base_urls = {
            "openai": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "anthropic": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "cohere": os.getenv("COHERE_BASE_URL", "https://api.cohere.ai"),
            "groq": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            "ollama": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "openrouter": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        }
        
        return base_urls.get(provider.lower())
    
    @staticmethod
    def list_supported_providers() -> list:
        """List all supported provider names."""
        return [
            "openai",
            "anthropic", 
            "cohere",
            "groq",
            "ollama",
            "google",
            "gemini",
            "openrouter"
        ]
    
    @staticmethod
    def is_provider_available(provider: str) -> bool:
        """Check if a provider is available (dependencies installed)."""
        try:
            LLMProviderFactory.create_provider(provider)
            return True
        except (ImportError, ValueError):
            return False
