#!/usr/bin/env python3
"""
Simple test for system prompt handling in call_ai.
Run this to quickly verify the new functionality works.
"""

import aiwand
from dotenv import load_dotenv

def main():
    load_dotenv()

    print("🧪 Quick System Prompt Test")
    print("=" * 40)
    
    # Test 1: Empty system prompt
    print("\n1. Testing empty system prompt...")
    try:
        response = aiwand.call_ai(
            messages=[{"role": "user", "content": "Say hello briefly"}],
            system_prompt="",  # Empty string should be respected
            temperature=0.3
        )
        print(f"✅ Empty prompt response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Messages with existing system message
    print("\n2. Testing existing system message in conversation...")
    try:
        messages_with_system = [
            {"role": "system", "content": "You are a helpful assistant that answers in one word."},
            {"role": "user", "content": "What color is the sky?"}
        ]
        response = aiwand.call_ai(
            messages=messages_with_system,
            system_prompt="This should be ignored",  # Should NOT be used
            temperature=0.3
        )
        print(f"✅ Existing system response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Custom system prompt
    print("\n3. Testing custom system prompt...")
    try:
        response = aiwand.call_ai(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a robot. Say 'BEEP BOOP' before everything.",
            temperature=0.3
        )
        print(f"✅ Custom prompt response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: System prompt only (no messages)
    print("\n4. Testing system prompt only (no messages)...")
    try:
        response = aiwand.call_ai(
            system_prompt="Write a small joke about programming.",
            temperature=0.7,
            model="gemini-2.0-flash-lite"
        )
        print(f"✅ System prompt only response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Empty messages with system prompt
    print("\n5. Testing empty messages list with system prompt...")
    try:
        response = aiwand.call_ai(
            messages=[],
            system_prompt="You are a helpful assistant. Generate a fun fact about space.",
            temperature=0.5
        )
        print(f"✅ Empty messages response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Quick test complete!")

if __name__ == "__main__":
    main() 