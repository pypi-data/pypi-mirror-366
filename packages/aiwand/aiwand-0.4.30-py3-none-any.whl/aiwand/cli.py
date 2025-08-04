"""
Command Line Interface for AIWand
"""

import argparse
import json
import sys
from .core import summarize, chat, generate_text
from .extract import extract
from .models import AIError
from .setup import setup_user_preferences, show_current_config
from .helper import find_chrome_binary, get_chrome_version, generate_random_number, generate_uuid
from .classifier import classify_text



def main():
    """Main CLI entry point."""
    # Check if this is a direct prompt (only works with quoted text containing spaces/punctuation)
    known_commands = {'summarize', 'chat', 'generate', 'classify', 'extract', 'setup', 'status', 'helper'}
    
    # Handle non-command arguments
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith('-'):
        
        if len(sys.argv) == 2:
            # Single argument case: aiwand "something" or aiwand something
            single_arg = sys.argv[1]
            
            # Only treat as direct prompt if it contains spaces (indicating it was quoted)
            # Single words without spaces are rejected to avoid command confusion
            if ' ' in single_arg:
                # Multi-word content - must have been quoted
                try:
                    result = chat(message=single_arg)
                    print(result)
                    return
                except AIError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Single word - show error
                print(f"Error: '{single_arg}' is not a recognized command.", file=sys.stderr)
                print("For single-word prompts, use the chat command:", file=sys.stderr)
                print(f"  aiwand chat \"{single_arg}\"", file=sys.stderr)
                print("For available commands, use: aiwand --help", file=sys.stderr)
                sys.exit(1)
                
        else:
            # Multiple unquoted words - show error
            attempted_prompt = ' '.join(sys.argv[1:])
            print(f"Error: Unquoted multi-word input detected.", file=sys.stderr)
            print(f"Did you mean: aiwand \"{attempted_prompt}\"", file=sys.stderr)
            print("Direct prompts must be quoted to avoid confusion with commands.", file=sys.stderr)
            sys.exit(1)
    
    # Original subcommand-based CLI logic
    parser = argparse.ArgumentParser(
        description="AIWand - AI toolkit for text processing\n\nQuick usage: aiwand \"Your multi-word prompt here\" for direct chat\n(Single words require: aiwand chat \"word\")",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize text')
    summarize_parser.add_argument('text', help='Text to summarize')
    summarize_parser.add_argument('--style', choices=['concise', 'detailed', 'bullet-points'], 
                                 default='concise', help='Summary style')
    summarize_parser.add_argument('--max-length', type=int, help='Maximum length in words')
    summarize_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with AI')
    chat_parser.add_argument('message', help='Message to send')
    chat_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    chat_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate text from prompt')
    generate_parser.add_argument('prompt', help='Prompt for text generation')
    generate_parser.add_argument('--max-tokens', type=int, default=500, help='Maximum tokens to generate')
    generate_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    generate_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Classify command
    classify_parser = subparsers.add_parser('classify', help='Classify or grade text responses')
    classify_parser.add_argument('question', help='The question, prompt, or context')
    classify_parser.add_argument('answer', help='The response to evaluate')
    classify_parser.add_argument('--expected', default='', help='Expected response for comparison')
    classify_parser.add_argument('--choices', help='Choice scores as JSON (e.g., \'{"A":1.0,"B":0.5,"C":0.0}\')')
    classify_parser.add_argument('--prompt', help='Custom prompt template')
    classify_parser.add_argument('--no-reasoning', action='store_true', help='Skip step-by-step reasoning')
    classify_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive setup for preferences')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current configuration')
    
    # Helper command
    helper_parser = subparsers.add_parser('helper', help='Utility functions for development and testing')
    helper_subparsers = helper_parser.add_subparsers(dest='helper_command', help='Helper utilities')
    
    # Random number generator
    random_parser = helper_subparsers.add_parser('random', help='Generate random numbers')
    random_parser.add_argument('--length', type=int, default=6, help='Number of digits (default: 6)')
    random_parser.add_argument('--count', type=int, default=1, help='Number of random numbers to generate (default: 1)')
    
    # UUID generator
    uuid_parser = helper_subparsers.add_parser('uuid', help='Generate UUIDs')
    uuid_parser.add_argument('--version', type=int, choices=[1, 4], default=4, help='UUID version (1 or 4, default: 4)')
    uuid_parser.add_argument('--uppercase', action='store_true', help='Generate uppercase UUID')
    uuid_parser.add_argument('--count', type=int, default=1, help='Number of UUIDs to generate (default: 1)')
    
    # Chrome binary finder
    chrome_parser = helper_subparsers.add_parser('chrome', help='Find Chrome browser executable')
    chrome_parser.add_argument('--version', action='store_true', help='Also show Chrome version')
    chrome_parser.add_argument('--path-only', action='store_true', help='Output only the path (no quotes, for scripting)')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract structured data from content and/or links')
    extract_parser.add_argument('content', nargs='?', help='Content to extract from (any format - will be converted to string)')
    extract_parser.add_argument('--links', nargs='*', 
                               help='URLs or file paths to read and include in extraction')
    extract_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    extract_parser.add_argument('--temperature', type=float, default=0.7, 
                               help='Response creativity (0.0-1.0, default 0.7)')
    extract_parser.add_argument('--json', action='store_true', 
                               help='Force JSON output')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'summarize':
            result = summarize(
                text=args.text,
                max_length=args.max_length,
                style=args.style,
                model=args.model
            )
            print(result)
            
        elif args.command == 'chat':
            result = chat(
                message=args.message,
                model=args.model,
                temperature=args.temperature
            )
            print(result)
            
        elif args.command == 'generate':
            result = generate_text(
                prompt=args.prompt,
                max_output_tokens=args.max_output_tokens,
                temperature=args.temperature,
                model=args.model
            )
            print(result)
            
        elif args.command == 'classify':
            try:
                choices = json.loads(args.choices) if args.choices else None
                result = classify_text(
                    question=args.question,
                    answer=args.answer,
                    expected_response=args.expected,
                    choices=choices,
                    custom_prompt=args.prompt,
                    no_reasoning=args.no_reasoning,
                    model=args.model
                )
                print(json.dumps(result, indent=2))
            except json.JSONDecodeError:
                print("Error: Invalid JSON format for choices", file=sys.stderr)
                sys.exit(1)
                
        elif args.command == 'extract':
            try:
                # Check that we have either content or links
                if not args.content and not args.links:
                    print("Error: Must provide either content or --links", file=sys.stderr)
                    sys.exit(1)
                
                result = extract(
                    content=args.content,
                    links=args.links,
                    model=args.model,
                    temperature=args.temperature
                )
                
                # Format output
                if isinstance(result, dict) or args.json:
                    if isinstance(result, dict):
                        print(json.dumps(result, indent=2))
                    else:
                        # Try to parse as JSON for pretty printing
                        try:
                            parsed = json.loads(result)
                            print(json.dumps(parsed, indent=2))
                        except json.JSONDecodeError:
                            print(result)
                else:
                    print(result)
                    
            except FileNotFoundError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
                
        elif args.command == 'setup':
            setup_user_preferences()
            
        elif args.command == 'status':
            show_current_config()
            
        elif args.command == 'helper':
            if not args.helper_command:
                print("Error: Please specify a helper command. Use 'aiwand helper --help' for options.", file=sys.stderr)
                sys.exit(1)
                
            if args.helper_command == 'random':
                try:
                    for i in range(args.count):
                        number = generate_random_number(args.length)
                        print(number)
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
                    
            elif args.helper_command == 'uuid':
                try:
                    for i in range(args.count):
                        uuid_str = generate_uuid(version=args.version, uppercase=args.uppercase)
                        print(uuid_str)
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
                    
            elif args.helper_command == 'chrome':
                try:
                    chrome_path = find_chrome_binary()
                    
                    if args.path_only:
                        # Just output the raw path for scripting
                        print(chrome_path)
                    else:
                        # Output quoted path for easy copying
                        print(f'"{chrome_path}"')
                    
                    if args.version:
                        version = get_chrome_version(chrome_path)
                        if version:
                            print(f"Version: {version}")
                        else:
                            print("Version: Unable to determine")
                            
                except FileNotFoundError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
            
    except AIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 