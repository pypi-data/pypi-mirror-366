"""
Base and factory classes for LLM provider integration in ShaheenAI.

These classes provide the abstraction layer for various LLM provider
integrations such as OpenAI, Cohere, Ollama, and more.
"""

from typing import List, Dict, Any

class BaseLLMProvider:
    """
    Base class for LLM providers.
    Defines the interface for all providers.
    """
    
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: A list of messages with role and content
            **kwargs: Additional parameters specific to the provider

        Returns:
            A string response from the LLM
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Async version of generate method.

        Args:
            messages: A list of messages with role and content
            **kwargs: Additional parameters specific to the provider

        Returns:
            A string response from the LLM
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class LLMProviderFactory:
    """
    Factory class to create LLM provider instances based on configuration.
    """
    
    @staticmethod
    def create_provider(config: Any) -> BaseLLMProvider:
        """
        Create a provider instance based on the given configuration.

        Args:
            config: Provider configuration, typically a string or dict

        Returns:
            An instance of a subclass of BaseLLMProvider
        """
        provider_name = config if isinstance(config, str) else config.get("name")
        
        # Example logic for provider selection; customize based on actual providers
        if provider_name == "openai":
            from .openai import OpenAIProvider
            return OpenAIProvider(config)
        elif provider_name == "cohere":
            from .cohere import CohereProvider
            return CohereProvider(config)
        elif provider_name == "ollama":
            from .ollama import OllamaProvider
            return OllamaProvider(config)
        # Add additional provider cases as needed
        
        raise ValueError(f"Unsupported provider: {provider_name}")

