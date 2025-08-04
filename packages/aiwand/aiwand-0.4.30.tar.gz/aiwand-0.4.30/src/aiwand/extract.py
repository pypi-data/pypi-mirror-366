"""
Extract functionality for AIWand - structured data extraction from any content
"""

from typing import Optional, List, Union, Any, Dict
from pydantic import BaseModel
from .config import call_ai, ModelType
from .prompts import EXTRACT_SYSTEM_PROMPT
from .utils import (
    convert_to_string, string_to_json, fetch_all_data
)


def extract(
    content: Optional[Union[str, Any]] = None,
    links: Optional[List[str]] = None,
    document_links: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    model: Optional[ModelType] = None,
    temperature: float = 0.7,
    response_format: Optional[BaseModel] = None,
    system_prompt: Optional[str] = EXTRACT_SYSTEM_PROMPT,
    additional_system_instructions: Optional[str] = None,
    debug: Optional[bool] = False,
) -> Union[str, Dict[str, Any]]:
    """
    Extract structured data from content and/or links using AI.
    
    This function processes any content (converted to string) and fetches data from
    links (URLs or file paths), then extracts structured information using AI.
    
    Args:
        content: Any content to extract from - will be converted to string.
            Can be str, dict, list, or any object with __str__ method.
        links: List of web URLs or file paths to fetch and include in extraction.
            URLs (http/https) will be fetched, file paths will be read.
        document_links: List of document URLs to include in extraction.
        images: List of image URLs to include in extraction.
        model: Specific AI model to use (auto-selected if not provided)
        temperature: Response creativity (0.0 to 1.0, default 0.7)
        response_format: Pydantic model class for structured output.
        system_prompt: Custom system prompt to override the default extraction prompt.
        additional_system_instructions: Any other relavant instructions to help the extraction.
        
    Returns:
        Union[str, Dict[str, Any]]: Extracted data.
        - Dict if JSON parsing succeeds
        - Formatted string otherwise
        
    Raises:
        ValueError: If neither content nor links are provided
        AIError: If the AI call fails
        FileNotFoundError: If file path doesn't exist
        
    Examples:
        # Simple text extraction
        result = extract(content="John Doe, email: john@example.com")
        
        # Extract from URLs
        result = extract(links=["https://example.com/article"])
        
        # Mix content and links with structured output
        from pydantic import BaseModel
        
        class ContactInfo(BaseModel):
            name: str
            email: str
            
        result = extract(
            content="Meeting notes: contact John at john@example.com",
            links=["https://company.com/about", "/path/to/business_card.txt"],
            response_format=ContactInfo
        )
        
        # Complex content (dict/list converted to string)
        data = {"name": "John", "email": "john@example.com"}
        result = extract(content=data)
    """    
    all_content = []
    
    if content is not None:
        content_str = convert_to_string(content)
        if content_str.strip():
            all_content.append(f"=== Main Content ===\n{content_str}")
    
    if links:
        links_data = fetch_all_data(links=links)
        for link_data in links_data:
            url = link_data.url
            data = link_data.content
            all_content.append(f"=== URL {url} ===\n{data}\n")
        
    combined_content = "\n\n".join(all_content)

    if response_format:
        user_prompt = "Return the data as JSON format."    
    else:
        user_prompt = (
            "Use appropriate categories and present the information in a way that's "
            "easy to understand and use. Include any relevant metadata or context.\n\n"
        )    
    
    user_prompt += f"\n\nExtract relevant structured data from the following content:\n{combined_content}"
    
    result = call_ai(
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        response_format=response_format,
        user_prompt=user_prompt,
        additional_system_instructions=additional_system_instructions,
        images=images,
        document_links=document_links,
        debug=debug
    )
    if response_format:
        return result    
    return string_to_json(result)

