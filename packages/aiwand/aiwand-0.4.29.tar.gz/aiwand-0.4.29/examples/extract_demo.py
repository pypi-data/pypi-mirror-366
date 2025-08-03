#!/usr/bin/env python3
"""
Working demonstration of AIWand extract functionality.

This example loads environment variables and shows real extraction examples.
"""

import json
import sys
import os
from pathlib import Path

# Add the src directory to Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded")
except ImportError:
    print("⚠️  python-dotenv not installed, assuming environment variables are set")

from aiwand import extract


def demo_simple_text():
    """Demo: Extract from simple text content."""
    print("\n=== Simple Text Extraction ===")
    
    text = """
    Dr. Sarah Johnson is the Chief Technology Officer at InnovateLabs Inc.
    You can reach her at sarah.johnson@innovatelabs.com or call (415) 555-0123.
    The company is located at 1234 Innovation Drive, Palo Alto, CA 94301.
    She's organizing a tech conference on March 15, 2024 at 2:00 PM.
    """
    
    print("Input text:")
    print(text.strip())
    print()
    
    try:
        result = extract(content=text, debug=True)
        print("Extracted contact information:")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}")


def demo_mixed_content():
    """Demo: Extract from mixed content formats."""
    print("\n=== Mixed Content Extraction ===")
    
    # Different data formats
    meeting_notes = "Quick meeting with John Smith about Q4 budget planning"
    
    contact_data = {
        "name": "John Smith",
        "department": "Finance", 
        "email": "john.smith@company.com",
        "notes": "Scheduled follow-up for next week"
    }
    
    event_list = [
        "Budget review meeting - March 20, 2024",
        "Q4 planning session - March 25, 2024",
        "Team retrospective - March 30, 2024"
    ]
    
    print("Input data:")
    print(f"Meeting notes: {meeting_notes}")
    print(f"Contact data: {contact_data}")
    print(f"Events: {event_list}")
    print()
    
    try:
        # Extract from string
        result1 = extract(content=meeting_notes)
        
        # Extract from dict
        result2 = extract(content=contact_data)
        
        # Extract from list
        result3 = extract(content=event_list)
        
        print("Extracted from meeting notes:")
        print(json.dumps(result1, indent=2) if isinstance(result1, dict) else result1)
        print()
        
        print("Extracted from contact data:")
        print(json.dumps(result2, indent=2) if isinstance(result2, dict) else result2)
        print()
        
        print("Extracted from event list:")
        print(json.dumps(result3, indent=2) if isinstance(result3, dict) else result3)
        
    except Exception as e:
        print(f"Error: {e}")


def demo_file_extraction():
    """Demo: Extract from file content."""
    print("\n=== File Extraction ===")
    
    # Create a sample file
    sample_file = Path("sample_business_card.txt")
    sample_content = """
    BUSINESS CARD
    
    Michael Chen
    Senior Software Engineer
    TechCorp Solutions
    
    📧 michael.chen@techcorp.com
    📱 (555) 987-6543
    🌐 www.techcorp.com
    
    📍 456 Tech Street, Suite 200
    San Francisco, CA 94105
    
    Specializing in AI/ML solutions and cloud architecture
    """
    
    try:
        # Write sample file
        sample_file.write_text(sample_content)
        print(f"Created sample file: {sample_file}")
        print()
        
        # Extract from file
        result = extract(links=[str(sample_file)])
        
        print("Extracted from business card:")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()
            print(f"\nCleaned up: {sample_file}")


def demo_combined_sources():
    """Demo: Extract from multiple sources combined."""
    print("\n=== Combined Sources Extraction ===")
    
    # Main content
    content = "Meeting summary: Discussed partnership with TechStart Inc."
    
    # Create sample files
    file1 = Path("company_info.txt")
    file2 = Path("contact_details.txt")
    
    file1_content = """
    TechStart Inc. - AI Innovation Company
    Founded in 2020, specializing in machine learning solutions
    CEO: Jennifer Walsh
    Location: Seattle, WA
    """
    
    file2_content = """
    Contact Information:
    Jennifer Walsh - CEO
    Email: jennifer@techstart.com
    Phone: (206) 555-0199
    Assistant: Maria Rodriguez (maria@techstart.com)
    """
    
    try:
        # Write sample files
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        print("Content:", content)
        print(f"File 1 ({file1}): Company information")
        print(f"File 2 ({file2}): Contact details")
        print()
        
        # Extract from combined sources
        result = extract(
            content=content,
            links=[str(file1), str(file2)]
        )
        
        print("Extracted partnership information:")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        for file in [file1, file2]:
            if file.exists():
                file.unlink()
        print(f"\nCleaned up sample files")


def main():
    """Run all demonstrations."""
    print("AIWand Extract - Working Examples")
    print("=" * 50)
    
    # Check if we have API keys
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_gemini = bool(os.getenv('GEMINI_API_KEY'))
    
    if not (has_openai or has_gemini):
        print("⚠️  No API keys found!")
        print("Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable")
        print("You can create a .env file with:")
        print("OPENAI_API_KEY=your_key_here")
        print("# or")
        print("GEMINI_API_KEY=your_key_here")
        return
    
    print(f"✓ OpenAI API key: {'Present' if has_openai else 'Not set'}")
    print(f"✓ Gemini API key: {'Present' if has_gemini else 'Not set'}")
    
    # Run demonstrations
    demos = [
        demo_simple_text,
        demo_mixed_content,
        demo_file_extraction,
        demo_combined_sources,
    ]
    
    for demo in demos:
        try:
            demo()
            print("\n" + "-" * 50)
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("-" * 50)
    
    print("\n🎉 Extract examples completed!")
    print("\nTry the CLI:")
    print('aiwand extract "John Doe, john@example.com" --type contact_info')


if __name__ == "__main__":
    main() 