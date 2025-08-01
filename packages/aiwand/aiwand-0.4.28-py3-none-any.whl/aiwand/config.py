"""
Core AI functionality for AIWand.

This module provides the main AI request functionality, client management,
and provider resolution utilities.
"""

import os
import base64
import json
import mimetypes
from pathlib import Path  
from typing import Dict, Any, Optional, Tuple, List, Union
from google.genai import (
    Client as GeminiClient
)
from openai import OpenAI

from .prompts import DEFAULT_SYSTEM_PROMPT
from .models import (
    AIProvider,
    ModelType,
    GeminiModel,
    ProviderRegistry,
    AIError
)
from .preferences import get_preferred_provider_and_model
from .utils import (
    image_to_data_url,
    retry_with_backoff,
    get_gemini_response,
    remove_empty_values,
    print_debug_messages,
    get_openai_response,
    fetch_doc
)

# Client cache to avoid recreating clients
_client_cache: Dict[AIProvider, Union[OpenAI, GeminiClient]] = {}



def _get_cached_client(provider: AIProvider) -> Union[OpenAI, GeminiClient]:
    """Get or create a cached client for the provider."""
    if provider not in _client_cache:
        # Get provider configuration from registry
        env_var = ProviderRegistry.get_env_var(provider)
        base_url = ProviderRegistry.get_base_url(provider)
        
        if not env_var:
            raise AIError(f"Unsupported provider: {provider}")
        
        api_key = os.getenv(env_var)
        if not api_key:
            raise AIError(f"{provider.value.title()} API key not found. Please set {env_var} environment variable.")

        if provider == AIProvider.GEMINI:
            _client_cache[provider] = GeminiClient(api_key=api_key)
        elif base_url:
            _client_cache[provider] = OpenAI(api_key=api_key, base_url=base_url)
        else:
            _client_cache[provider] = OpenAI(api_key=api_key)
    
    return _client_cache[provider]


def _resolve_provider_model_client(
    model: Optional[ModelType] = None, 
    provider: Optional[Union[AIProvider, str]] = None
) -> Tuple[AIProvider, str, OpenAI]:
    """
    Resolve provider, model name, and client based on input model, provider, or preferences.
    
    Args:
        model: Optional model to use for inference
        provider: Optional provider to use explicitly (AIProvider enum or string)
        
    Returns:
        Tuple of (provider, model_name, client)
        
    Raises:
        AIError: When no provider is available
    """
    # Handle explicit provider specification
    if provider is not None:
        # Convert string to AIProvider enum if needed
        if isinstance(provider, str):
            try:
                provider_enum = AIProvider(provider.lower())
            except ValueError:
                raise AIError(f"Unknown provider: {provider}. Supported providers: {[p.value for p in AIProvider]}")
        else:
            provider_enum = provider
        
        # Use explicit provider with provided model or get default model for provider
        if model is not None:
            return provider_enum, str(model), _get_cached_client(provider_enum)
        else:
            default_model = ProviderRegistry.get_default_model(provider_enum)
            if not default_model:
                raise AIError(f"No default model available for provider: {provider_enum}")
            return provider_enum, str(default_model), _get_cached_client(provider_enum)
    
    # No explicit provider, try to infer from model
    if model is not None:
        # Try to infer provider from model (now includes pattern matching)
        inferred_provider = ProviderRegistry.infer_provider_from_model(model)
        if inferred_provider is not None:
            return inferred_provider, str(model), _get_cached_client(inferred_provider)
        else:
            # Model provided but can't infer provider, use preferences with provided model
            fallback_provider, _ = get_preferred_provider_and_model()
            if not fallback_provider:
                raise AIError("No AI provider available. Please set up your API keys.")
            return fallback_provider, str(model), _get_cached_client(fallback_provider)
    else:
        # No model or provider provided, use current preferences
        pref_provider, preferred_model = get_preferred_provider_and_model()
        if not pref_provider or not preferred_model:
            raise AIError("No AI provider available. Please set up your API keys and run 'aiwand setup'.")
        return pref_provider, str(preferred_model), _get_cached_client(pref_provider)


@retry_with_backoff(max_retries=2)
def call_ai(
    messages: Optional[List[Dict[str, str]]] = None,
    max_output_tokens: Optional[int] = None,
    temperature: float = 0.7,
    top_p: float = 1.0,
    model: Optional[ModelType] = GeminiModel.GEMINI_2_0_FLASH_LITE.value,
    provider: Optional[Union[AIProvider, str]] = None,
    response_format: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
    additional_system_instructions: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    document_links: Optional[List[str]] = None,
    reasoning_effort: Optional[str] = None,
    tool_choice: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    debug: Optional[bool] = False,
    use_google_search: Optional[bool] = False
) -> str:
    """
    Unified wrapper for AI API calls that handles provider differences.
    
    Args:
        messages: Optional list of message dictionaries with 'role' and 'content'.
                 If None or empty, a default user message will be added.
        max_output_tokens: Maximum tokens to generate
        temperature: Response creativity (0.0 to 1.0)
        top_p: Nucleus sampling parameter
        model: Specific model to use (auto-selected if not provided)
        provider: Optional provider to use explicitly (AIProvider enum or string like 'openai', 'gemini').
                 Overrides model-based inference when specified.
        response_format: Response format specification
        system_prompt: Optional system prompt to add at the beginning (uses default if None).
                      Can be used alone without messages for simple generation.
        user_prompt: Optional user message to add at the end of the messages list.
                     Can be used in parallel with or without existing messages.
        additional_system_instructions: Optional additional instructions to append to the system prompt.
                                       If provided, will be added to the end of the system message with proper spacing.
        images: Optional list of images to add to the messages list.
                Can be a list of strings (URLs), Path objects, or bytes.
        reasoning_effort: Optional reasoning effort to use for the AI call.
                          Can be "low", "medium", "high".
        tool_choice: Optional tool choice to use for the AI call.
                     Can be "auto", "none", "required".
        tools: Optional list of tools to use for the AI call.
               Can be a list of tool dictionaries with 'type', 'function', and 'description'.
        use_google_search: Optional boolean to use google search tool.
                Only works with Gemini models.
    Returns:
        str: The AI response content
        
    Raises:
        AIError: When the API call fails
    """
    try:
        # Resolve provider, model, and client
        current_provider, model_name, client = _resolve_provider_model_client(model, provider)
        
        # Handle case where messages is None or empty
        if messages is None:
            messages = []
        
        # Prepare messages with system prompt
        final_messages = messages.copy()
        
        # Check if messages already contain a system message
        has_system_message = any(msg.get("role") == "system" for msg in final_messages)
        
        # Add system prompt only if:
        # 1. No existing system message in messages
        # 2. Either system_prompt was explicitly provided (including empty string) or we should use default
        if not has_system_message:
            final_messages.insert(0, {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT})

        # Append additional system instructions if provided
        if additional_system_instructions is not None:
            # Find the system message and append additional instructions
            for msg in final_messages:
                if msg.get("role") == "system":
                    current_content = msg["content"]
                    # Add proper spacing if current content exists and doesn't end with whitespace
                    if current_content:
                        msg["content"] = f"{current_content}\n\n{additional_system_instructions}"
                    break

        if user_prompt is not None:
            final_messages.append({"role": "user", "content": user_prompt})
        
        # If we only have a system message (no user messages), add a default user message
        # This allows using system_prompt alone as a kind of generation prompt
        has_user_message = any(msg.get("role") in ["user", "assistant"] for msg in final_messages)
        if not has_user_message:
            final_messages.append({"role": "user", "content": "Please respond based on the instructions."})

        if images:
            image_parts = [
                {"type": "image_url", "image_url": {"url": image_to_data_url(img)}}
                for img in images
            ]
            final_messages.append({"role": "user", "content": image_parts})

        if document_links:
            document_parts = []
            for url in document_links:
                fetched_data = fetch_doc(url)
                mime_type, _ = mimetypes.guess_type(url)
                if isinstance(fetched_data, str):
                    base64_string = base64.b64encode(fetched_data.encode('utf-8')).decode('utf-8')
                else:
                    base64_string = base64.b64encode(fetched_data).decode('utf-8')
                doc_part = {
                    "type": "input_file",
                    "filename": url.split("/")[-1],
                    "file_data": f"data:{mime_type};base64,{base64_string}",
                }
                document_parts.append(doc_part)
            final_messages.append({"role": "user", "content": document_parts})

        # Prepare common parameters
        params = {
            "model": model_name,
            "messages": final_messages,
            "temperature": temperature,
            "top_p": top_p,
            "tool_choice": tool_choice,
            "tools": tools,
            "max_completion_tokens": max_output_tokens,
            # "reasoning_effort": reasoning_effort,
            "response_format": response_format,
        }
        remove_empty_values(params=params)

        content = None
        if current_provider == AIProvider.GEMINI:
            params["use_google_search"] = use_google_search
            content = get_gemini_response(client, params, debug)
        elif current_provider == AIProvider.OPENAI:
            content = get_openai_response(client, params, debug)
        else:
            content = get_chat_completions_response(client, params, debug=debug)
        return content
    except AIError as e:
        raise AIError(str(e))
    except Exception as e:
        raise AIError(f"AI request failed: {str(e)}")


def get_chat_completions_response(client: OpenAI, params: Dict[str, Any], debug: bool = False) -> str:
    if debug:
        print_debug_messages(messages=params.get("messages"), params=params)
    response = client.chat.completions.create(**params)
    content = response.choices[0].message.content.strip()
    response_format = params.get("response_format")
    if response_format:
        if isinstance(content, dict):
            parsed = content
        else:
            parsed = json.loads(content)
        return response_format(**parsed)
    return content


def list_models(provider: Optional[AIProvider] = None):
    client = get_ai_client(provider)
    models = client.models.list()
    return models


def get_ai_client(provider: Optional[AIProvider] = None) -> OpenAI:
    """
    Get configured AI client with smart provider selection.
    
    Returns:
        OpenAI: Configured client for the selected provider
        
    Raises:
        AIError: When no API provider is available
    """
    if provider is None:
        provider, _ = get_preferred_provider_and_model()
    
    if not provider:
        available = ProviderRegistry.get_available_providers()
        if not any(available.values()):
            raise AIError(
                "No API keys found. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable, "
                "or run 'aiwand setup' to configure your preferences."
            )
    
    return _get_cached_client(provider)

