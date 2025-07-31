"""
LLM interface for the Metis Agent Framework.
Provides a unified interface to multiple LLM providers.
"""
from typing import Optional, Dict, Any, List
from ..llm.factory import LLMFactory
from ..llm.base import BaseLLM
from ..auth.api_key_manager import APIKeyManager

# Global LLM instance
_llm_instance = None

def configure_llm(
    provider: str, 
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
):
    """
    Configure the global LLM instance.
    
    Args:
        provider: LLM provider name
        model: Model name
        api_key: API key
        **kwargs: Additional arguments for the LLM
    """
    global _llm_instance
    _llm_instance = LLMFactory.create(provider, model, api_key, **kwargs)
    
def get_llm(config=None) -> BaseLLM:
    """
    Get the global LLM instance.
    If not configured, tries to create one using available API keys or config.
    
    Args:
        config: Optional AgentConfig instance to get provider preferences
    
    Returns:
        LLM instance
    """
    global _llm_instance
    
    if _llm_instance is None:
        key_manager = APIKeyManager()
        
        # Get provider preference from config if available
        preferred_provider = None
        preferred_model = None
        
        if config:
            preferred_provider = config.get("llm_provider", "groq")
            preferred_model = config.get("llm_model")
        
        # Try preferred provider first if specified and has key
        if preferred_provider and key_manager.has_key(preferred_provider):
            try:
                _llm_instance = LLMFactory.create(preferred_provider, preferred_model)
                print(f"+ Using configured LLM: {preferred_provider}")
                return _llm_instance
            except Exception as e:
                print(f"Warning: Could not create configured {preferred_provider} LLM: {e}")
        
        # Try providers in order of preference
        providers = ["groq", "anthropic", "huggingface", "openai"]
        if preferred_provider and preferred_provider not in providers:
            providers.insert(0, preferred_provider)
            
        for provider in providers:
            if key_manager.has_key(provider):
                try:
                    _llm_instance = LLMFactory.create(provider)
                    print(f"+ Using available LLM: {provider}")
                    break
                except Exception as e:
                    print(f"Warning: Could not create {provider} LLM: {e}")
                    
        if _llm_instance is None:
            # No LLM could be configured - provide helpful error message
            error_msg = (
                "No LLM provider configured. Please set up an API key using one of these commands:\n"
                "  metis auth set groq <your-groq-api-key>\n"
                "  metis auth set anthropic <your-anthropic-api-key>\n"
                "  metis auth set openai <your-openai-api-key>\n"
                "  metis auth set huggingface <your-hf-api-key>\n\n"
                "You can get API keys from:\n"
                "  - Groq: https://console.groq.com/keys\n"
                "  - Anthropic: https://console.anthropic.com/\n"
                "  - OpenAI: https://platform.openai.com/api-keys\n"
                "  - HuggingFace: https://huggingface.co/settings/tokens"
            )
            raise ValueError(error_msg)
            
    return _llm_instance


def reset_llm():
    """
    Reset the global LLM instance to force reconfiguration.
    Useful when configuration changes.
    """
    global _llm_instance
    _llm_instance = None