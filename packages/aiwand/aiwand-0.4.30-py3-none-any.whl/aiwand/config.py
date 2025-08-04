"""
Core AI functionality for AIWand.

This module provides the main AI request functionality, client management,
and provider resolution utilities.
"""

import os
import json
from pathlib import Path  
from typing import Dict, Any, Optional, Tuple, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.genai import (
    Client as GeminiClient
)
from openai import OpenAI

from .prompts import DEFAULT_SYSTEM_PROMPT, OCR_SYSTEM_PROMPT
from .models import (
    AIProvider,
    ModelType,
    GeminiModel,
    ProviderRegistry,
    AIError,
    OCRContentType
)
from .preferences import get_preferred_provider_and_model
from .utils import (
    image_to_data_url,
    document_to_data_url,
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


def process_single_ocr(
    content,
    content_type: OCRContentType,
    index: int,
    total_count: int,
    ocr_system_prompt: str,
    ocr_additional_system_instructions: Optional[str] = None,
    model: Optional[ModelType] = None,
    debug: Optional[bool] = False
) -> Optional[Tuple[int, str]]:
    """
    Process a single item (image or document) for OCR extraction.
    
    Args:
        content: Content to process (image or document)
        content_type: Type of content (OCRContentType.IMAGE or OCRContentType.DOCUMENT)
        index: Index of the item (0-based)
        total_count: Total number of items being processed
        ocr_system_prompt: System prompt for OCR
        model: Model to use for OCR
        
    Returns:
        Tuple of (index, extracted_text) or None if extraction failed
    """
    try:
        # Prepare the call based on content type
        call_kwargs = {
            "system_prompt": ocr_system_prompt or OCR_SYSTEM_PROMPT,
            "user_prompt": f"Please extract all text from this {content_type.value}:",
            "model": model,
            "additional_system_instructions": ocr_additional_system_instructions,
            "use_ocr": False,
            "use_vision": True,
            "debug": debug
        }
        if content_type == OCRContentType.IMAGE:
            call_kwargs["images"] = [content]
            item_name = f"{index+1}"
        else:  # OCRContentType.DOCUMENT
            call_kwargs["document_links"] = [content]
            if isinstance(content, str) and ("/" in content or "\\" in content):
                item_name = content.split("/")[-1] if "/" in content else content.split("\\")[-1]
            else:
                item_name = f"document_{index+1}"

        # Process the content
        extracted_text = call_ai(**call_kwargs)
        
        if extracted_text.strip():
            # Add identifier if multiple items
            if total_count > 1:
                type_label = content_type.value.title()
                if content_type == OCRContentType.DOCUMENT and item_name != f"document_{index+1}":
                    formatted_text = f"=== {type_label}: {item_name} ===\n{extracted_text.strip()}"
                else:
                    formatted_text = f"=== {type_label} {index+1} ===\n{extracted_text.strip()}"
            else:
                formatted_text = extracted_text.strip()
            return (index, formatted_text)
        return None
                
    except Exception as e:
        content_name = content_type.value
        print(f"Warning: OCR extraction failed for {content_name} {index+1}: {e}")
        return None


def ocr(
    system_prompt: Optional[str] = None,
    additional_system_instructions: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    document_links: Optional[List[str]] = None,
    model: Optional[ModelType] = None,
    max_workers: Optional[int] = None,
    debug: Optional[bool] = False
) -> str:
    """
    Extract text from images and/or documents using OCR via AI vision model.
    Processes items in parallel for improved performance.
    
    Args:
        images: Optional list of images to extract text from
        document_links: Optional list of document paths/URLs to extract text from
        model: Optional model to use for OCR
        max_workers: Optional maximum number of parallel workers (default: min(10, num_items))
        
    Returns:
        str: Extracted text from all items, formatted and concatenated
    """
    extracted_texts = []
    total_items = (len(images) if images else 0) + (len(document_links) if document_links else 0)
    
    if total_items == 0:
        return ""
    
    if debug:
        print(f"Extracting text using OCR from {total_items} items in parallel...")

    ocr_system_prompt = system_prompt or OCR_SYSTEM_PROMPT 
       
    # Calculate optimal number of workers
    if max_workers is None:
        # Limit to 10 workers max to avoid overwhelming the API, but use fewer for small batches
        max_workers = min(10, max(1, total_items))
    
    all_results = []
    
    # Process images in parallel if provided
    if images:
        if debug:
            print(f"Processing {len(images)} images in parallel...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all image processing tasks
            future_to_index_images = {
                executor.submit(process_single_ocr, image, OCRContentType.IMAGE, i, len(images), ocr_system_prompt, additional_system_instructions, model, debug): i
                for i, image in enumerate(images)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index_images):
                result = future.result()
                if result is not None:
                    all_results.append(result)
    
    # Process documents in parallel if provided
    if document_links:
        if debug:
            print(f"Processing {len(document_links)} documents in parallel...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all document processing tasks
            future_to_index_documents = {
                executor.submit(process_single_ocr, doc_link, OCRContentType.DOCUMENT, i, len(document_links), ocr_system_prompt, additional_system_instructions, model, debug): i
                for i, doc_link in enumerate(document_links)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index_documents):
                result = future.result()
                if result is not None:
                    all_results.append(result)
    
    # Sort results by original index to maintain order
    all_results.sort(key=lambda x: x[0])
    
    # Extract just the text content
    extracted_texts = [result[1] for result in all_results]
    
    if debug:
        print(f"OCR extraction completed. Processed {len(extracted_texts)}/{total_items} items successfully.")
    
    return "\n\n".join(extracted_texts)


@retry_with_backoff(max_retries=2)
def call_ai(
    messages: Optional[List[Dict[str, str]]] = None,
    max_output_tokens: Optional[int] = None,
    temperature: float = 0.7,
    top_p: float = 1.0,
    model: Optional[ModelType] = GeminiModel.GEMINI_2_5_FLASH_LITE.value,
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
    use_google_search: Optional[bool] = False,
    use_ocr: Optional[bool] = True,
    use_vision: Optional[bool] = False,
    max_workers: Optional[int] = None
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
        use_ocr: Optional boolean to extract text from images/documents using OCR before processing.
                 When True, images and documents will be processed for text extraction and added as context.
        use_vision: Optional boolean to use direct vision capabilities (current default behavior).
                   When False with use_ocr=True, only extracted text will be sent, not the raw images.
        max_workers: Optional maximum number of parallel workers for OCR processing.
                    Only applies when use_ocr=True. Default: min(10, num_items).
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

        # Handle OCR extraction if requested
        ocr_context = ""
        if use_ocr and (images or document_links):
            extracted_text = ocr(
                images=images, 
                document_links=document_links, 
                model=model, 
                max_workers=max_workers,
                additional_system_instructions=additional_system_instructions,
                debug=debug
            )
            if extracted_text.strip():
                ocr_context = f"\n{extracted_text}\n"

        # Add OCR context to the last user message if available
        if len(ocr_context) > 0:
            final_messages.append({"role": "user", "content": f"<content>{ocr_context}</context>"})

        # Handle images (only add raw images if use_vision=True or use_ocr=False)
        if images and (use_vision or not use_ocr):
            image_parts = [
                {"type": "image_url", "image_url": {"url": image_to_data_url(img)}}
                for img in images
            ]
            final_messages.append({"role": "user", "content": image_parts})

        # Handle documents (only add raw documents if use_vision=True or use_ocr=False)
        if document_links and (use_vision or not use_ocr):
            document_parts = []
            for doc_src in document_links:
                # Use the new document_to_data_url function that handles binary, URLs, and file paths
                try:
                    data_url = document_to_data_url(doc_src)
                    # Extract filename for display purposes
                    if isinstance(doc_src, str) and ("/" in doc_src or "\\" in doc_src):
                        filename = doc_src.split("/")[-1] if "/" in doc_src else doc_src.split("\\")[-1]
                    else:
                        filename = "document"                    
                    doc_part = {
                        "type": "input_file",
                        "filename": filename,
                        "file_data": data_url,
                    }
                    document_parts.append(doc_part)
                except Exception as e:
                    print(f"Warning: Failed to process document {doc_src}: {e}")
                    continue
            
            if len(document_parts) > 0:
                final_messages.append({"role": "user", "content": document_parts})

        has_user_message = any(msg.get("role") in ["user", "assistant"] for msg in final_messages)
        if not has_user_message:
            final_messages.append({"role": "user", "content": "Please respond based on the instructions."})

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

