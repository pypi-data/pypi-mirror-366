#!/usr/bin/env python3
"""
Simple test for system prompt handling in call_ai.
This version uses the local aiwand source code directly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path to use local aiwand
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import aiwand
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("🧪 Quick System Prompt Test (Using Local Source)")
    print("=" * 50)
    print(f"Using aiwand from: {aiwand.__file__}")
    print(f"AIWand version: {aiwand.__version__}")
    
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

    # Test 4: Custom system prompt
    print("\n4. Testing custom system prompt... and response format")
    try:
        response = aiwand.call_ai(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="You are a robot. Say 'BEEP BOOP' before everything.",
            temperature=0.3
        )
        print(f"✅ Custom prompt response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Quick test complete!")

if __name__ == "__main__":
    main() 