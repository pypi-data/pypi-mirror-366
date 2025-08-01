from typing import Dict, Any, List, Optional
import base64
import re
import mimetypes
from google.genai import (
    client as gemini_client,
    types as gemini_types
)
from pydantic import BaseModel

from .extras import remove_empty_values
from .llm_utils import get_system_msg
from .web_utils import fetch_doc


def get_gemini_config(params: Dict[str, Any]) -> gemini_types.GenerateContentConfig:
    """
    Get configuration for the Gemini API.
    """
    config_dict = {
        "temperature": params.get("temperature"),
        "top_p": params.get("top_p"),
        "top_k": params.get("top_k"),
        "max_output_tokens": params.get("max_completion_tokens"),
        "system_instruction": get_system_msg(params.get("messages", [])),
        "response_modalities": ['TEXT'],
        "tools": params.get("tools"),
        "tool_config": params.get("tool_config")
    }

    if params.get("use_google_search"):
        grounding_tool = gemini_types.Tool(
            google_search=gemini_types.GoogleSearch()
        )
        tools = params.get("tools", [])
        if tools:
            config_dict["tools"] = [
                *tools,
                grounding_tool
            ]
        else:
            config_dict["tools"] = [grounding_tool]
    
    # Handle structured output
    response_format: Optional[BaseModel] = params.get("response_format")
    if response_format:
        config_dict["response_schema"] = response_format.model_json_schema()
        config_dict["response_mime_type"] = "application/json"
    
    # Remove empty values and create config
    cleaned_config = remove_empty_values(config_dict)
    return gemini_types.GenerateContentConfig(**cleaned_config)


def _parse_data_url(data_url: str) -> tuple[bytes, str]:
    """
    Parse a data URL and return (data_bytes, mime_type).
    
    Args:
        data_url: Data URL in format "data:mime/type;base64,data"
        
    Returns:
        tuple of (data_bytes, mime_type)
    """
    # Pattern to match data URLs: data:mime/type;base64,data
    pattern = r'^data:([^;]+);base64,(.+)$'
    match = re.match(pattern, data_url)
    
    if not match:
        raise ValueError(f"Invalid data URL format: {data_url[:50]}...")
    
    mime_type = match.group(1)
    base64_data = match.group(2)
    
    try:
        data_bytes = base64.b64decode(base64_data)
        return data_bytes, mime_type
    except Exception as e:
        raise ValueError(f"Failed to decode base64 data: {e}")


def _convert_content_to_parts(content: Any) -> List[gemini_types.Part]:
    """
    Convert OpenAI-style content to Gemini Parts.
    
    Args:
        content: Can be a string or list of content items
        
    Returns:
        List of Gemini Parts
    """
    parts = []
    
    if isinstance(content, str):
        # Simple text content
        if content.strip():
            parts.append(gemini_types.Part.from_text(text=content))
    elif isinstance(content, list):
        # List of content items (text and/or images/documents)
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if text.strip():
                        parts.append(gemini_types.Part.from_text(text=text))
                elif item.get("type") == "input_text":
                    text = item.get("text", "")
                    if text.strip():
                        parts.append(gemini_types.Part.from_text(text=text))
                elif item.get("type") == "image_url":
                    image_url_data = item.get("image_url", {})
                    url = image_url_data.get("url", "")
                    if url.startswith("data:"):
                        # It's a data URL, convert to bytes
                        try:
                            data_bytes, mime_type = _parse_data_url(url)
                            parts.append(gemini_types.Part.from_bytes(
                                data=data_bytes,
                                mime_type=mime_type
                            ))
                        except ValueError as e:
                            print(f"Warning: Failed to process image data URL: {e}")
                    else:
                        parts.append(gemini_types.Part.from_uri(file_uri=url, mime_type=""))
                elif item.get("type") == "input_file":
                    # Handle document files
                    if "file_data" in item:
                        # Base64 encoded file data
                        file_data = item.get("file_data", "")
                        filename = item.get("filename", "")
                        
                        if file_data.startswith("data:"):
                            # Parse data URL format: data:mime/type;base64,data
                            try:
                                data_bytes, mime_type = _parse_data_url(file_data)
                                parts.append(gemini_types.Part.from_bytes(
                                    data=data_bytes,
                                    mime_type=mime_type
                                ))
                            except ValueError as e:
                                print(f"Warning: Failed to process file data URL for {filename}: {e}")
                        else:
                            # Assume it's raw base64 data, try to guess mime type from filename
                            try:
                                data_bytes = base64.b64decode(file_data)
                                # Guess mime type from filename extension
                                mime_type, _ = mimetypes.guess_type(filename)
                                if not mime_type:
                                    # Default to PDF if we can't guess
                                    mime_type = "application/pdf"
                                
                                parts.append(gemini_types.Part.from_bytes(
                                    data=data_bytes,
                                    mime_type=mime_type
                                ))
                            except Exception as e:
                                print(f"Warning: Failed to process base64 file data for {filename}: {e}")
                    
                    elif "file_url" in item:
                        # Remote file URL - fetch content and convert to inline data
                        file_url = item.get("file_url", "")
                        if file_url:
                            try:
                                fetched_data = fetch_doc(file_url)
                                if fetched_data:
                                    # Convert fetched content to bytes
                                    if isinstance(fetched_data, str):
                                        # For text-like content, encode as UTF-8
                                        data_bytes = fetched_data.encode('utf-8')
                                        mime_type = "text/plain"
                                    else:
                                        # For binary content
                                        data_bytes = fetched_data
                                        # Guess mime type from URL extension
                                        mime_type, _ = mimetypes.guess_type(file_url)
                                        if not mime_type:
                                            # Default to PDF if we can't guess
                                            mime_type = "application/pdf"
                                    
                                    parts.append(gemini_types.Part.from_bytes(
                                        data=data_bytes,
                                        mime_type=mime_type
                                    ))
                                else:
                                    print(f"Warning: Failed to fetch content from file URL: {file_url}")
                            except Exception as e:
                                print(f"Warning: Failed to process file URL {file_url}: {e}")
            elif isinstance(item, str):
                # Plain string in the list
                if item.strip():
                    parts.append(gemini_types.Part.from_text(text=item))
    else:
        # Fallback: convert to string
        text = str(content)
        if text.strip():
            parts.append(gemini_types.Part.from_text(text=text))
    
    return parts


def get_gemini_contents(messages: List[Dict[str, Any]]) -> List[gemini_types.Content]:
    """
    Convert OpenAI-style messages to Gemini Contents.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        
    Returns:
        List of Gemini Content objects
    """
    contents = []
    
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        
        # Skip system messages as they're handled in config
        if role == "system":
            continue
            
        # Convert content to parts
        parts = _convert_content_to_parts(content)
        
        # Skip empty messages
        if not parts:
            continue
        
        # Create appropriate content type based on role
        if role == "user":
            contents.append(gemini_types.UserContent(parts=parts))
        elif role == "assistant":
            contents.append(gemini_types.ModelContent(parts=parts))
        else:
            # Fallback: treat unknown roles as user content
            contents.append(gemini_types.UserContent(parts=parts))
    
    return contents


def get_gemini_response(client: gemini_client, params: Dict[str, Any], debug: bool = False) -> str:
    """
    Get a response from the Gemini API.
    
    Args:
        client: Gemini client instance
        params: Parameters including model, messages, and config options
        
    Returns:
        AI response content as string
    """
    model = params.get("model")
    messages = params.get("messages", [])
    
    config = get_gemini_config(params)
    contents = get_gemini_contents(messages)

    response_format = params.get("response_format")

    if debug:
        print('params', params)
        print('model', model)
        print('contents', contents)
        print('config', config)
    
    response = client.models.generate_content(
        model=model, 
        contents=contents, 
        config=config
    )

    if response_format:
        return response_format(**response.parsed)
    return response.text

