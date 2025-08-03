"""
AIWand - A simple AI toolkit for text processing using OpenAI and Gemini
"""

__version__ = "0.4.29"
__author__ = "Aman Kumar"

from .core import summarize, chat, generate_text
from .extract import extract
from .config import (
    call_ai,
    get_ai_client,
    list_models
)
from .preferences import (
    get_current_provider,
    get_model_name
)
from .prompts import (
    DEFAULT_SYSTEM_PROMPT
)
from .setup import (
    setup_user_preferences, 
    show_current_config, 
)
from .models import (
    AIError,
    AIProvider,
    OpenAIModel,
    GeminiModel,
    ModelType,
    ProviderType,
    ProviderRegistry,
)
from .helper import (
    generate_random_number, 
    generate_uuid,
    # File and URL helpers (still used internally)
    get_file_extension,
    is_text_file,
)
from .utils import (
    fetch_data,
    fetch_all_data,
    read_file_content,
    is_remote_url,
)
from .classifier import (
    ClassifierResponse,
    classify_text,
    create_classifier,
    create_binary_classifier,
    create_quality_classifier,
)

__all__ = [
    # Core AI functions
    "summarize",
    "chat", 
    "generate_text",
    "extract",
    "call_ai",
    
    # Configuration and setup
    "setup_user_preferences",
    "show_current_config",
    "get_ai_client",
    "get_current_provider", 
    "get_model_name",
    "list_models",

    # AI Models and Providers
    "AIProvider",
    "OpenAIModel", 
    "GeminiModel",
    "ModelType",
    "ProviderType",
    "ProviderRegistry",
    
    # Helper functions
    "generate_random_number",
    "generate_uuid",
    "get_file_extension",
    "is_text_file",

    # utils
    "fetch_data",
    "read_file_content",
    "fetch_all_data", 
    "is_remote_url",
       
    # Classification
    "ClassifierResponse",
    "classify_text",
    "create_classifier", 
    "create_binary_classifier",
    "create_quality_classifier",
    
    # Configuration
    "AIError",
    "DEFAULT_SYSTEM_PROMPT",
] 