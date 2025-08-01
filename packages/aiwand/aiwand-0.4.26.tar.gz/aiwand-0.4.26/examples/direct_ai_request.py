#!/usr/bin/env python3
"""
Example demonstrating direct usage of call_ai function.

This shows how to use the low-level AI request function directly,
which provides maximum flexibility including response format handling,
custom system prompts, and automatic provider switching.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aiwand import (
    call_ai, 
    DEFAULT_SYSTEM_PROMPT, 
    AIError, 
    OpenAIModel, 
    GeminiModel,
    get_current_provider
)


def basic_request_example():
    """Basic usage of call_ai."""
    print("=== Basic AI Request ===")
    
    try:        
        response = call_ai(
            user_prompt="Explain quantum computing in one paragraph."
        )
        print(f"Response: {response}")
        
    except AIError as e:
        print(f"Error: {e}")


def custom_system_prompt_example():
    """Example with custom system prompt."""
    print("\n=== Custom System Prompt ===")
    
    try:        
        custom_system = "You are a technical expert who explains programming concepts with practical examples and code snippets."
        
        response = call_ai(
            system_prompt=custom_system,
            user_prompt="What is Python?"
            temperature=0.3  # Lower temperature for more focused technical responses
        )
        print(f"Response: {response}")
        
    except AIError as e:
        print(f"Error: {e}")


def conversation_example():
    """Example of maintaining conversation history."""
    print("\n=== Conversation History ===")
    
    try:
        # Start a conversation
        conversation = [
            {"role": "user", "content": "Hi, I'm learning about machine learning."},
        ]
        
        response1 = call_ai(
            messages=conversation,
            system_prompt="You are a patient ML tutor who provides clear explanations."
        )
        print(f"AI: {response1}")
        
        # Continue the conversation
        conversation.append({"role": "assistant", "content": response1})
        conversation.append({"role": "user", "content": "What's the difference between supervised and unsupervised learning?"})
        
        response2 = call_ai(
            messages=conversation,
            system_prompt="You are a patient ML tutor who provides clear explanations."
        )
        print(f"AI: {response2}")
        
    except AIError as e:
        print(f"Error: {e}")


def structured_response_example():
    """Example using response format for structured output."""
    print("\n=== Structured Response Format ===")
    
    try:
        messages = [
            {"role": "user", "content": "Analyze the pros and cons of remote work."}
        ]
        
        # Request JSON response format
        response_format = {
            "type": "json_object"
        }
        
        structured_system = """You are an analyst who provides structured responses. 
        Always respond with valid JSON in this format:
        {
            "topic": "the main topic",
            "pros": ["list", "of", "advantages"],
            "cons": ["list", "of", "disadvantages"],
            "conclusion": "brief summary"
        }"""
        
        response = call_ai(
            messages=messages,
            system_prompt=structured_system,
            response_format=response_format,
            temperature=0.7
        )
        print(f"Structured Response: {response}")
        
    except AIError as e:
        print(f"Error: {e}")
        print("Note: Structured output may not be supported by all providers/models")


def model_specific_example():
    """Example specifying a particular model."""
    print("\n=== Model-Specific Request ===")
    
    try:
        provider = get_current_provider()
        print(f"Current provider: {provider}")        
        
        # Try to use a specific model based on current provider
        if provider and "openai" in str(provider).lower():
            model = OpenAIModel.GPT_4O_MINI  # Fast and cost-effective
        else:
            model = GeminiModel.GEMINI_2_0_FLASH  # Fast Gemini model
            
        response = call_ai(
            model=model,
            system_prompt="You are a creative poet who writes beautiful, concise poetry.",
            user_prompt="Write a haiku about coding.",
            temperature=0.9  # Higher creativity for poetry
        )
        print(f"Haiku: {response}")
        
    except AIError as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("🪄 AIWand - Direct AI Request Examples")
    print("=" * 50)
    
    # Show current configuration
    try:
        provider = get_current_provider()
        print(f"Using provider: {provider}")
        print(f"Default system prompt: {DEFAULT_SYSTEM_PROMPT}")
        print()
    except Exception as e:
        print(f"Configuration info unavailable: {e}\n")
    
    # Run examples
    basic_request_example()
    custom_system_prompt_example()
    conversation_example()
    structured_response_example()
    model_specific_example()
    
    print("\n✅ Examples completed!")
    print("\n💡 Key Benefits of call_ai:")
    print("  • Automatic provider switching (OpenAI ↔ Gemini)")
    print("  • Built-in response format handling")
    print("  • Flexible system prompt management")
    print("  • Full conversation history support")
    print("  • Model-specific requests")
    print("  • Unified API across all providers")


if __name__ == "__main__":
    main() 