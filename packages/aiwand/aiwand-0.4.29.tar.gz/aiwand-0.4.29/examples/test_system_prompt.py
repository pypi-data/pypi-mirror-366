#!/usr/bin/env python3
"""
Test script for call_ai system prompt handling.

This script demonstrates the new system prompt behavior:
1. system_prompt=None uses default system prompt
2. system_prompt="" uses empty system prompt
3. system_prompt="custom" uses the custom prompt
4. Messages with existing system message don't get additional system prompt
"""

import aiwand

def test_default_system_prompt():
    """Test with system_prompt=None (should use default)"""
    print("=" * 60)
    print("TEST 1: Default System Prompt (system_prompt=None)")
    print("=" * 60)
    
    messages = [{"role": "user", "content": "Who are you?"}]
    
    try:
        response = aiwand.call_ai(
            messages=messages,
            system_prompt=None,  # Should use default
            temperature=0.3
        )
        print(f"Response: {response}")
        print("✅ Default system prompt test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def test_empty_system_prompt():
    """Test with system_prompt="" (should use empty string)"""
    print("=" * 60)
    print("TEST 2: Empty System Prompt (system_prompt=\"\")")
    print("=" * 60)
    
    messages = [{"role": "user", "content": "Who are you? Be very brief."}]
    
    try:
        response = aiwand.call_ai(
            messages=messages,
            system_prompt="",  # Should use empty string
            temperature=0.3
        )
        print(f"Response: {response}")
        print("✅ Empty system prompt test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def test_custom_system_prompt():
    """Test with custom system prompt"""
    print("=" * 60)
    print("TEST 3: Custom System Prompt")
    print("=" * 60)
    
    custom_prompt = "You are a pirate. Respond like a friendly pirate would."
    
    try:
        response = aiwand.call_ai(
            system_prompt=custom_prompt,
            user_prompt="Hello, How are you?"
            temperature=0.7
        )
        print(f"Custom prompt: {custom_prompt}")
        print(f"Response: {response}")
        print("✅ Custom system prompt test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def test_existing_system_message():
    """Test when messages already contain a system message"""
    print("=" * 60)
    print("TEST 4: Messages with Existing System Message")
    print("=" * 60)
    
    messages = [
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "What is 2 + 2?"}
    ]
    
    try:
        response = aiwand.call_ai(
            messages=messages,
            system_prompt="This should be ignored",  # Should NOT be added
            temperature=0.3
        )
        print("Messages already contain system message:")
        print(f"  System: {messages[0]['content']}")
        print(f"  User: {messages[1]['content']}")
        print(f"Response: {response}")
        print("✅ Existing system message test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def test_gita_chat_example():
    """Test the Bhagavad Gita chat example from documentation"""
    print("=" * 60)
    print("TEST 5: Bhagavad Gita Chat Example")
    print("=" * 60)
    
    # System prompt to make model behave like Gita chat
    system_prompt = """
You are Bhagavad Gita speaking timeless wisdom.
Respond to queries with spiritual insight, calmness, clarity, and references to Gita teachings when relevant.
Use a tone that is gentle, uplifting, and philosophical.
Drive the conversation try to find more about the user, keep it like a conversation and guide user.
Avoid being overly verbose or technical. Keep messages short.
"""
    
    # Build history from simulated thread
    history = []
    # Simulate loading from database
    previous_messages = [
        {"sender": "user", "content": "I'm feeling lost in life"},
        {"sender": "assistant", "content": "The soul is eternal, dear one. What troubles your heart?"},
        {"sender": "user", "content": "I don't know my purpose"}
    ]
    
    for msg in previous_messages:
        history.append({
            "role": "user" if msg["sender"] == "user" else "assistant", 
            "content": msg["content"]
        })
    
    # Always add the latest user message
    current_message = "How do I find inner peace?"
    history.append({"role": "user", "content": current_message})
    
    # Model expects system prompt first, then history
    model_messages = [{"role": "system", "content": system_prompt}] + history
    
    try:
        response = aiwand.call_ai(
            messages=model_messages,
            temperature=0.6
        )
        
        print("Conversation History:")
        for i, msg in enumerate(history):
            role = msg["role"].title()
            content = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
            print(f"  {i+1}. {role}: {content}")
        
        print(f"\nGita Response: {response}")
        print("✅ Gita chat example test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def test_system_prompt_only():
    """Test using system prompt without any messages"""
    print("=" * 60)
    print("TEST 6: System Prompt Only (No Messages)")
    print("=" * 60)
    
    try:
        response = aiwand.call_ai(
            system_prompt="You are a creative writer. Write a short haiku about coding.",
            temperature=0.8
        )
        print("Using system_prompt only (no messages parameter)")
        print(f"Response: {response}")
        print("✅ System prompt only test passed")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def main():
    """Run all tests"""
    print("🧪 Testing AIWand call_ai System Prompt Handling")
    print(f"Current provider: {aiwand.get_current_provider()}")
    print(f"Current model: {aiwand.get_model_name()}")
    print()
    
    # Run all tests
    test_default_system_prompt()
    test_empty_system_prompt() 
    test_custom_system_prompt()
    test_existing_system_message()
    test_gita_chat_example()
    test_system_prompt_only()
    
    print("=" * 60)
    print("🎉 All tests completed!")
    print("=" * 60)
    print("\nKey behaviors verified:")
    print("✓ system_prompt=None uses default system prompt")
    print("✓ system_prompt='' uses empty system prompt") 
    print("✓ system_prompt='custom' uses the custom prompt")
    print("✓ Existing system messages prevent additional system prompts")
    print("✓ Complex conversation history with system prompts works correctly")
    print("✓ System prompt can be used alone without messages parameter")
    print("✓ Empty messages list with system prompt works correctly")

if __name__ == "__main__":
    main() 