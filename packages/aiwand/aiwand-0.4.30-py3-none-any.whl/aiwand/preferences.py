"""
User preferences and configuration management for AIWand.

This module handles saving/loading user preferences, configuration files,
and preference-related utilities.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

from .models import (
    AIError,
    AIProvider,
    OpenAIModel,
    GeminiModel,
    ProviderRegistry,
)


def get_config_dir() -> Path:
    """Get the AIWand configuration directory."""
    config_dir = Path.home() / ".aiwand"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / "config.json"


def load_user_preferences() -> Dict[str, Any]:
    """Load user preferences from config file."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If config is corrupted, return empty dict
            pass
    return {}


def save_user_preferences(preferences: Dict[str, Any]) -> None:
    """Save user preferences to config file."""
    config_file = get_config_file()
    try:
        with open(config_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    except IOError as e:
        raise AIError(f"Failed to save preferences: {e}")


def get_preferred_provider_and_model() -> Tuple[Optional[AIProvider], Optional[Union[OpenAIModel, GeminiModel]]]:
    """Get user's preferred provider and model from preferences."""
    preferences = load_user_preferences()
    available_providers = ProviderRegistry.get_available_providers()
    
    # Get preferred provider
    preferred_provider_str = preferences.get("default_provider")
    preferred_provider = None
    
    if preferred_provider_str:
        try:
            preferred_provider = AIProvider(preferred_provider_str)
        except ValueError:
            preferred_provider = None
    
    # If preferred provider is not available, fall back to available ones
    if not preferred_provider or not available_providers.get(preferred_provider):
        # Check environment variable
        env_provider = os.getenv("AI_DEFAULT_PROVIDER", "").lower()
        try:
            env_provider_enum = AIProvider(env_provider)
            if available_providers.get(env_provider_enum):
                preferred_provider = env_provider_enum
        except ValueError:
            pass
        
        if not preferred_provider:
            # Use first available provider
            for provider, available in available_providers.items():
                if available:
                    preferred_provider = provider
                    break
    
    if not preferred_provider:
        return None, None
    
    # Get preferred model for the provider
    preferred_model_str = preferences.get("models", {}).get(preferred_provider.value)
    preferred_model = None
    
    if preferred_model_str:
        # Use registry to get model enum
        preferred_model = ProviderRegistry.get_model_enum(preferred_provider, preferred_model_str)
        if preferred_model is None:
            # Fall back to default if model string is invalid
            preferred_model = ProviderRegistry.get_default_model(preferred_provider)
    else:
        preferred_model = ProviderRegistry.get_default_model(preferred_provider)
    
    return preferred_provider, preferred_model 


def get_current_provider() -> Optional[AIProvider]:
    """Get the currently active provider."""
    provider, _ = get_preferred_provider_and_model()
    return provider


def get_model_name() -> str:
    """
    Get the model name for the current provider.
    
    Returns:
        str: Model name to use
        
    Raises:
        AIError: When no provider is available
    """
    _, model = get_preferred_provider_and_model()
    
    if not model:
        raise AIError(
            "No AI provider available. Please set up your API keys and run 'aiwand setup' "
            "to configure your preferences."
        )
    
    return str(model) 


