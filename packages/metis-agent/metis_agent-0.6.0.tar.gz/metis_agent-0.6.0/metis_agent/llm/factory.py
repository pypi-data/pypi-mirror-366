"""
LLM Factory for Metis Agent.

This module provides a factory for creating LLM instances.
"""
from typing import Optional, Dict, Any
from .base import BaseLLM


class LLMFactory:
    """
    Factory for creating LLM instances.
    """
    
    @staticmethod
    def create(
        provider: str, 
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """
        Create an LLM instance.
        
        Args:
            provider: LLM provider name
            model: Model name (if None, uses default for provider)
            api_key: API key (if None, tries to get from APIKeyManager)
            **kwargs: Additional arguments for the LLM
            
        Returns:
            LLM instance
        """
        provider = provider.lower()
        
        if provider == "openai":
            from .openai_llm import OpenAILLM
            return OpenAILLM(model=model or "gpt-4o", api_key=api_key, **kwargs)
        elif provider == "groq":
            from .groq_llm import GroqLLM
            return GroqLLM(model=model or "llama3-70b-8192", api_key=api_key, **kwargs)
        elif provider == "anthropic":
            from .anthropic_llm import AnthropicLLM
            return AnthropicLLM(model=model or "claude-3-opus-20240229", api_key=api_key, **kwargs)
        elif provider == "huggingface":
            from .huggingface_llm import HuggingFaceLLM
            return HuggingFaceLLM(model=model or "mistralai/Mixtral-8x7B-Instruct-v0.1", api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")