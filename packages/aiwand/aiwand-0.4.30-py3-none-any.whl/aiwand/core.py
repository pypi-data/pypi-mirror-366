"""
Core AI functionality for AIWand
"""

from typing import Optional, List, Dict
from .config import call_ai, ModelType
from .prompts import (
    SUMMARIZE_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT,
    GENERATE_TEXT_SYSTEM_PROMPT
)


def summarize(
    text: str,
    max_length: Optional[int] = None,
    style: str = "concise",
    model: Optional[ModelType] = None
) -> str:
    """
    Summarize the given text using AI API (OpenAI or Gemini).
    
    Args:
        text (str): The text to summarize
        max_length (Optional[int]): Maximum length of the summary in words
        style (str): Style of summary ('concise', 'detailed', 'bullet-points')
        model (Optional[ModelType]): Specific model to use (auto-selected if not provided)
        
    Returns:
        str: The summarized text
        
    Raises:
        ValueError: If the text is empty
        AIError: If the API call fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    style_prompts = {
        "concise": "Provide a concise summary of the following text:",
        "detailed": "Provide a detailed summary of the following text:",
        "bullet-points": "Summarize the following text in bullet points:"
    }
    
    user_prompt = style_prompts.get(style, style_prompts["concise"])
    
    if max_length:
        user_prompt += f" Keep the summary under {max_length} words."
    
    return call_ai(
        model=model,
        system_prompt=SUMMARIZE_SYSTEM_PROMPT,
        user_prompt=f"{user_prompt}\n\n{text}"
    )


def chat(
    message: str,
    system_prompt: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model: Optional[ModelType] = None,
    temperature: float = 0.7
) -> str:
    """
    Have a conversation with the AI (OpenAI or Gemini).
    
    Args:
        message (str): The user's message
        conversation_history (Optional[List[Dict[str, str]]]): Previous conversation messages
        model (Optional[ModelType]): Specific model to use (auto-selected if not provided)
        temperature (float): Response creativity (0.0 to 1.0)
        
    Returns:
        str: The AI's response
        
    Raises:
        ValueError: If the message is empty
        AIError: If the API call fails
    """
    if not message.strip():
        raise ValueError("Message cannot be empty")
    
    messages = conversation_history or []
    
    return call_ai(
        messages=messages,
        temperature=temperature,
        model=model,
        system_prompt=system_prompt or CHAT_SYSTEM_PROMPT,
        user_prompt=message
    )


def generate_text(
    prompt: str,
    max_output_tokens: int = None,
    temperature: float = 0.7,
    model: Optional[ModelType] = None
) -> str:
    """
    Generate text based on a prompt using AI (OpenAI or Gemini).
    
    Args:
        prompt (str): The prompt to generate text from
        max_output_tokens (int): Maximum number of tokens to generate
        temperature (float): Response creativity (0.0 to 1.0)
        model (Optional[ModelType]): Specific model to use (auto-selected if not provided)
        
    Returns:
        str: The generated text
        
    Raises:
        ValueError: If the prompt is empty
        AIError: If the API call fails
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    return call_ai(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        model=model,
        system_prompt=GENERATE_TEXT_SYSTEM_PROMPT,
        user_prompt=prompt
    ) 
