"""
Interactive setup and configuration display for AIWand.

This module provides user-facing setup utilities and configuration display functions.
"""

from .models import AIError, AIProvider, ProviderRegistry
from .preferences import (
    load_user_preferences,
    save_user_preferences,
    get_preferred_provider_and_model,
    get_config_file
)


def setup_user_preferences() -> None:
    """Interactive setup for user preferences."""
    print("🪄 AIWand Setup")
    print("=" * 40)
    
    available_providers = ProviderRegistry.get_available_providers()
    available_list = [p for p, available in available_providers.items() if available]
    
    if not available_list:
        print("❌ No API keys found!")
        print("\nPlease set up your API keys first:")
        print("  OPENAI_API_KEY=your_openai_key")
        print("  GEMINI_API_KEY=your_gemini_key")
        print("\nThen run 'aiwand setup' again.")
        return
    
    print(f"📋 Available providers: {', '.join([p.value for p in available_list])}")
    
    # Load current preferences
    current_prefs = load_user_preferences()
    current_provider_str = current_prefs.get("default_provider")
    current_models = current_prefs.get("models", {})
    
    print(f"\nCurrent settings:")
    if current_provider_str:
        print(f"  Provider: {current_provider_str}")
        if current_provider_str in current_models:
            print(f"  Model: {current_models[current_provider_str]}")
    else:
        print("  No preferences set")
    
    # Choose provider
    print(f"\n🔧 Choose your default provider:")
    for i, provider in enumerate(available_list, 1):
        marker = " (current)" if provider.value == current_provider_str else ""
        print(f"  {i}. {provider.value.title()}{marker}")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(available_list)}) or press Enter to keep current: ").strip()
            if not choice and current_provider_str:
                chosen_provider_enum = AIProvider(current_provider_str)
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(available_list):
                chosen_provider_enum = available_list[int(choice) - 1]
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return
    
    # Choose model for the provider
    supported_models = ProviderRegistry.get_models_for_provider(chosen_provider_enum)
    current_model_str = current_models.get(chosen_provider_enum.value)
    default_model = ProviderRegistry.get_default_model(chosen_provider_enum)
    
    # Find current model enum or use default
    current_model_enum = default_model
    if current_model_str:
        model_enum = ProviderRegistry.get_model_enum(chosen_provider_enum, current_model_str)
        if model_enum is not None:
            current_model_enum = model_enum
    
    print(f"\n🤖 Choose your default model for {chosen_provider_enum.value.title()}:")
    for i, model in enumerate(supported_models, 1):
        marker = " (current)" if model == current_model_enum else ""
        if model == default_model:
            marker += " (recommended)"
        print(f"  {i}. {model.value}{marker}")
    
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(supported_models)}) or press Enter to keep current: ").strip()
            if not choice:
                chosen_model_enum = current_model_enum
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(supported_models):
                chosen_model_enum = supported_models[int(choice) - 1]
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return
    
    # Save preferences
    new_preferences = {
        "default_provider": chosen_provider_enum.value,
        "models": {
            **current_models,
            chosen_provider_enum.value: chosen_model_enum.value
        }
    }
    
    try:
        save_user_preferences(new_preferences)
        print(f"\n✅ Preferences saved!")
        print(f"   Provider: {chosen_provider_enum.value}")
        print(f"   Model: {chosen_model_enum.value}")
        print(f"\n💡 You can change these anytime by running 'aiwand setup'")
        print(f"📁 Config saved to: {get_config_file()}")
    except AIError as e:
        print(f"\n❌ Error saving preferences: {e}")


def show_current_config() -> None:
    """Display current configuration and preferences."""
    print("🪄 AIWand Configuration")
    print("=" * 40)
    
    # Show available providers
    available = ProviderRegistry.get_available_providers()
    print("📋 Available providers:")
    for provider, is_available in available.items():
        status = "✅" if is_available else "❌"
        print(f"  {status} {provider.value.title()}")
    
    if not any(available.values()):
        print("\n❌ No API keys configured!")
        print("Please set OPENAI_API_KEY or GEMINI_API_KEY environment variables.")
        return
    
    # Show current preferences
    preferences = load_user_preferences()
    print(f"\n⚙️  Current preferences:")
    
    if preferences:
        default_provider = preferences.get("default_provider")
        models = preferences.get("models", {})
        
        if default_provider:
            print(f"  Default provider: {default_provider}")
            if default_provider in models:
                print(f"  Default model: {models[default_provider]}")
        else:
            print("  No default provider set")
            
        if models:
            print(f"  Configured models:")
            for provider, model in models.items():
                print(f"    {provider}: {model}")
    else:
        print("  No preferences configured")
    
    # Show what will be used
    try:
        provider, model = get_preferred_provider_and_model()
        if provider and model:
            print(f"\n🎯 Currently using:")
            print(f"  Provider: {provider}")
            print(f"  Model: {model}")
        else:
            print(f"\n🎯 No provider currently available")
    except Exception as e:
        print(f"\n❌ Error getting current config: {e}")
    
    print(f"\n📁 Config file: {get_config_file()}")
    print(f"💡 Run 'aiwand setup' to change preferences") 