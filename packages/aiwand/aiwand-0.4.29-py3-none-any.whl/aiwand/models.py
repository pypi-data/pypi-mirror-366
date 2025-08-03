"""
AI Models and Providers for AIWand.

This module defines all supported AI providers and their models in an extensible
registry-based system that makes it easy to add new providers and models.
"""

import os
from enum import Enum
from typing import Dict, List, Union, Optional, Type, Any
from pydantic import BaseModel


class AIError(Exception):
    """Custom exception for AI-related errors."""
    pass


class LinkContent(BaseModel):
    url: str
    content: str


class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    
    def __str__(self) -> str:
        return self.value


class BaseModel(Enum):
    """Base class for AI models."""
    
    def __str__(self) -> str:
        return self.value


class OpenAIModel(BaseModel):
    """Supported OpenAI models."""

    O4_MINI = "o4-mini"
    O4_MINI_DEEP_RESEARCH = "o4-mini-deep-research"

    O3_PRO = "o3-pro"
    O3_DEEP_RESEARCH = "o3-deep-research"
    O3_MINI = "o3-mini"
    O3 = "o3"

    O1_PRO = "o1-pro"
    O1 = "o1"
    O1_PREVIEW = "o1-preview"

    CODEX_MINI = "codex-mini-latest"

    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CHATGPT_4O_LATEST = "chatgpt-4o-latest"

    GPT_IMAGE_1 = "gpt-image-1"
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"    

    WHISPER_1 = "whisper-1"
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    TTS_1_1106 = "tts-1-1106"
    TTS_1_HD_1106 = "tts-1-hd-1106"

    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_16k = "gpt-3.5-turbo-16k"

    TEXT_EMBEDDING_ADA_2 = "text-embedding-ada-002"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"



class GeminiModel(BaseModel):
    """Supported Gemini models."""
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_FLASH_LITE = "gemini-2.5-flash-lite-preview-06-17"
    GEMINI_LIVE_2_5_FLASH_PREVIEW = "gemini-live-2.5-flash-preview"
    GEMINI_LIVE_2_0_FLASH_LIVE = "gemini-2.0-flash-live-001"
    GEMINI_EMBEDDINGS_001 = "gemini-embedding-001"

    VEO_2 = "veo-2.0-generate-001"
    VEO_3 = "veo-3.0-generate-preview"
    IMAGEN_3 = "imagen-3.0-generate-002"
    IMAGEN_4 = "imagen-4.0-generate-preview-06-06"
    IMAGEN_4_ULTRA = "imagen-4.0-ultra-generate-preview-06-06"
    
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_PRO = "gemini-2.0-pro"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_0_FLASH_PREVIEW_IMAGE_GENERATION = "gemini-2.0-flash-preview-image-generation"
    
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH_8b = "gemini-1.5-flash-8b"


# Type aliases for models
ModelType = Union[OpenAIModel, GeminiModel, str]
ProviderType = Union[AIProvider, str]


# Provider Registry - Makes it easy to add new providers
class ProviderRegistry:
    """Registry system for AI providers and their configurations."""
    
    # Maps providers to their model classes
    PROVIDER_MODELS: Dict[AIProvider, Type[BaseModel]] = {
        AIProvider.OPENAI: OpenAIModel,
        AIProvider.GEMINI: GeminiModel,
    }
    
    # Default models for each provider
    PROVIDER_DEFAULTS: Dict[AIProvider, BaseModel] = {
        AIProvider.OPENAI: OpenAIModel.GPT_4O,  # Flagship multimodal model
        AIProvider.GEMINI: GeminiModel.GEMINI_2_0_FLASH,  # Stable, fast model
    }
    
    # Environment variables for API keys
    PROVIDER_ENV_VARS: Dict[AIProvider, str] = {
        AIProvider.OPENAI: "OPENAI_API_KEY",
        AIProvider.GEMINI: "GEMINI_API_KEY",
    }
    
    # Base URLs for each provider (None means use default)
    PROVIDER_BASE_URLS: Dict[AIProvider, Optional[str]] = {
        AIProvider.OPENAI: None,
        AIProvider.GEMINI: "https://generativelanguage.googleapis.com/v1beta/openai/",
    }
    
    @classmethod
    def get_all_providers(cls) -> List[AIProvider]:
        """Get list of all supported providers."""
        return list(cls.PROVIDER_MODELS.keys())
    
    @classmethod
    def get_models_for_provider(cls, provider: AIProvider) -> List[BaseModel]:
        """Get all models for a specific provider."""
        model_class = cls.PROVIDER_MODELS.get(provider)
        if model_class:
            return list(model_class)
        return []
    
    @classmethod
    def get_default_model(cls, provider: AIProvider) -> Optional[BaseModel]:
        """Get the default model for a provider."""
        return cls.PROVIDER_DEFAULTS.get(provider)
    
    @classmethod
    def get_env_var(cls, provider: AIProvider) -> Optional[str]:
        """Get the environment variable name for a provider's API key."""
        return cls.PROVIDER_ENV_VARS.get(provider)
    
    @classmethod
    def get_base_url(cls, provider: AIProvider) -> Optional[str]:
        """Get the base URL for a provider's API."""
        return cls.PROVIDER_BASE_URLS.get(provider)
    
    @classmethod
    def is_provider_available(cls, provider: AIProvider) -> bool:
        """Check if a provider is available (has API key set)."""
        env_var = cls.get_env_var(provider)
        if env_var:
            return bool(os.getenv(env_var))
        return False
    
    @classmethod
    def get_available_providers(cls) -> Dict[AIProvider, bool]:
        """Get availability status for all providers."""
        return {
            provider: cls.is_provider_available(provider)
            for provider in cls.get_all_providers()
        }
    
    @classmethod
    def infer_provider_from_model(cls, model: ModelType) -> Optional[AIProvider]:
        """
        Infer the AI provider from a model name.
        
        Args:
            model: Model name or enum to check
            
        Returns:
            AIProvider if model belongs to a known provider, None otherwise
        """
        model_str = str(model).lower()
        
        # First, check exact matches in our registry
        for provider, model_class in cls.PROVIDER_MODELS.items():
            try:
                model_class(str(model))  # Use original case for enum lookup
                return provider
            except ValueError:
                continue
        
        # If exact match fails, use pattern-based inference as fallback
        if "gemini" in model_str:
            return AIProvider.GEMINI
        
        # Could add more patterns here:
        # if "claude" in model_str or "opus" in model_str:
        #     return AIProvider.ANTHROPIC  # When we add Anthropic support
        
        return None
    
    @classmethod
    def get_model_enum(cls, provider: AIProvider, model_str: str) -> Optional[BaseModel]:
        """
        Get the model enum for a provider and model string.
        
        Args:
            provider: The AI provider
            model_str: Model name as string
            
        Returns:
            Model enum if valid, None otherwise
        """
        model_class = cls.PROVIDER_MODELS.get(provider)
        if model_class:
            try:
                return model_class(model_str)
            except ValueError:
                pass
        return None


# Convenience functions for backward compatibility and ease of use
def get_all_providers() -> List[AIProvider]:
    """Get list of all supported providers."""
    return ProviderRegistry.get_all_providers()


def get_models_for_provider(provider: AIProvider) -> List[BaseModel]:
    """Get all models for a specific provider."""
    return ProviderRegistry.get_models_for_provider(provider)


def get_default_model(provider: AIProvider) -> Optional[BaseModel]:
    """Get the default model for a provider."""
    return ProviderRegistry.get_default_model(provider)


def infer_provider_from_model(model: ModelType) -> Optional[AIProvider]:
    """Infer the AI provider from a model name."""
    return ProviderRegistry.infer_provider_from_model(model)


def is_provider_available(provider: AIProvider) -> bool:
    """Check if a provider is available (has API key set)."""
    return ProviderRegistry.is_provider_available(provider)


def get_available_providers() -> Dict[AIProvider, bool]:
    """Get availability status for all providers."""
    return ProviderRegistry.get_available_providers()


# Legacy compatibility - these functions maintain the old API
def get_supported_models() -> Dict[AIProvider, List[Union[OpenAIModel, GeminiModel]]]:
    """Get supported models for each provider (legacy compatibility)."""
    return {
        provider: ProviderRegistry.get_models_for_provider(provider)
        for provider in ProviderRegistry.get_all_providers()
    }


def get_default_models() -> Dict[AIProvider, Union[OpenAIModel, GeminiModel]]:
    """Get default models for each provider (legacy compatibility)."""
    return {
        provider: ProviderRegistry.get_default_model(provider)
        for provider in ProviderRegistry.get_all_providers()
        if ProviderRegistry.get_default_model(provider) is not None
    } 