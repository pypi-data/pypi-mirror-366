# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.29] - 2025-08-02
- Add Google genai pip as requirement

## [0.4.28] - 2025-08-01
- Fix image MIME type detection for bytes and data URLs

## [0.4.27] - 2025-08-01
- Refactor extract system prompt

## [0.4.26] - 2025-07-31
- Add *system_prompt* to chat

## [0.4.25] - 2025-07-25
- Add *use_google_search* to call_ai
- Add *google_search* tool to Gemini

## [0.4.24] - 2025-07-25
- Add *system_msg* to classifier
- Update Classifier Logic

## [0.4.23] - 2025-07-23
- Use document_data instead of document_links

## [0.4.22] - 2025-07-23
- Fix Gemini document_links handling
- Updated doc_test

## [0.4.21] - 2025-07-23
- Add *system_instructions* to extract
- Update README

## [0.4.20] - 2025-07-23
- Add *fetch_doc* for documents
- Add Document Understanding
- Update Openai to use responses api.

## [0.4.19] - 2025-07-22
- Add *debug* to extract
- Use genai for Gemini

## [0.4.18] - 2025-07-20
- Add *is_remote_url* function to utils
- Update methods to use *is_remote_url*

## [0.4.17] - 2025-07-20
- Fix Images Param in call_ai
- Add *debug* to call_ai
- Add *images* to extract
- Fix Bug in extract

## [0.4.16] - 2025-07-20
- Update fetch_data to ues full_text (title, url, text)
- Add get_soup function to web_utils

## [0.4.15] - 2025-07-20
- Move Utils, Prompts Around
- Refactor package

## [0.4.14] - 2025-07-20
- list_models
- Update Openai, Gemini Models

## [0.4.13] - 2025-07-20
- Added *list_models* function
- Updated *get_ai_client* function to accept AiProvider

## [0.4.12] - 2025-07-20
- Added *additional_system_instructions* parameter to *extract* function
- Updated aiwand.extract prompt instrucitons
- Fix is_local_file functionality

## [0.4.11] - 2025-07-20
- Minor Changes
- Changed fetch_url_content -> fetch_data
- Added *fetch_all_data*

## [0.4.10] - 2025-07-20

### 🔧 Core Improvements
- **API Refactoring**: Replaced legacy `make_ai_request` with unified `call_ai` function
  - Consolidated all AI request functionality into single entry point
  - Improved consistency across the codebase
  - Enhanced maintainability and code clarity
- **Configuration Streamlining**: Removed provider parameter from `get_model_name()`
  - Simplified function signature for better usability
  - Automatic provider resolution based on preferences
- **Code Organization**: General refactoring improvements
  - Enhanced code structure and readability
  - Improved internal function organization

## [0.4.8] - 2025-07-20

### 🎯 New Data Extraction Functionality
- **Structured Data Extraction**: Complete extract system for processing any content with AI
  - `aiwand.extract()` - Extract structured data from text, files, and URLs
  - Smart content conversion: Handles str, dict, list, or any object with __str__ method
  - Multi-source processing: Combine content with multiple URLs and file paths
  - Pydantic integration: Use `response_format` parameter for structured output objects
  - Automatic JSON parsing: Returns dict when possible, formatted string otherwise
- **Flexible Input Sources**: 
  - Text content: Direct string input or any convertible object
  - URLs: Automatic fetching and processing of web content
  - Files: Read local files and include in extraction context
  - Mixed sources: Combine content + links for comprehensive extraction
- **CLI Integration**: New `aiwand extract` command with full parameter support
  - `aiwand extract "content"` - Extract from text
  - `aiwand extract --links "url1" "url2"` - Extract from URLs/files
  - `--model`, `--temperature`, `--json` options for customization
- **Comprehensive Documentation**: 
  - Updated README with extract examples and structured output patterns
  - Complete API reference documentation with all parameters and examples
  - CLI reference with usage patterns and options
- **Robust Implementation**: 
  - Proper error handling for failed URL fetches and invalid files
  - Smart temperature defaults (0.7) for balanced creativity/consistency
  - Clean parameter interface without deprecated options
- **Updated Examples**: Fixed all demo files and tests to use correct parameter structure

## [0.4.7] - 2025-07-20

### 🧹 Simplified Classifier Interface
- **Consistent Parameter Naming**: Streamlined classifier interface to use only `question`, `answer`, `expected`
  - Removed confusing aliases: `input_text`, `output_text`, `expected_text` 
  - Single, clear naming convention throughout the entire API
  - Self-documenting function calls: `grader(question="...", answer="...", expected="...")`
- **Updated Templates**: Changed prompt placeholders from `{input}/{output}` to `{question}/{answer}`
- **CLI Improvements**: Updated `aiwand classify` command to use clear argument names
- **Comprehensive Documentation**: Updated all examples, docs, and help text to use consistent naming
- **Backward Compatibility**: Maintains functionality while providing much clearer interface

## [0.4.6] - 2025-07-20

### 🎯 New Classifier Functionality
- **Text Classification & Grading**: Complete classifier system inspired by autoevals
  - `aiwand.classify_text()` - Main classification function with custom criteria
  - `aiwand.create_classifier()` - Create reusable classifiers with predefined settings  
  - `aiwand.create_binary_classifier()` - Simple correct/incorrect classification
  - `aiwand.create_quality_classifier()` - A-F grading system
  - `ClassifierResponse` - Structured response with score, choice, reasoning, and metadata
- **Dramatic Simplification**: Replace complex KayLLMClassifier setup with one-line calls
  - Before: Multi-step setup with custom classes and async calls
  - After: `aiwand.classify_text(input_text, output_text, expected_text, choice_scores)`
- **CLI Integration**: New `aiwand classify` command with full parameter support
- **Provider Integration**: Uses existing OpenAI/Gemini provider system with structured output
- **Comprehensive Documentation**: Added classifier section to DEV-README.md and CLI docs
- **Examples**: Created `classifier_usage.py` and `classifier_test_basic.py` examples

## [0.4.5] - 2025-07-20

### 📚 Major Documentation Update
- **Enhanced README**: Complete rewrite focusing on simple migration value proposition
  - Lead with drop-in replacement story for existing AI code
  - Emphasize automatic Pydantic parsing with no post-processing needed
  - Showcase unified API working seamlessly across OpenAI and Gemini
  - Position `call_ai` as the core functionality
  - Add comprehensive examples for structured output handling
- **Migration-Focused Messaging**: Clear before/after code examples showing one-line changes
- **Improved Developer Experience**: Better organized sections with practical examples
- **Value Proposition Clarity**: Highlight key benefits of unified AI interface

## [0.4.4] - 2025-07-19

### ✨ Enhanced Provider Intelligence
- **Smart Pattern-Based Inference**: Added fallback provider detection for unknown models
  - Models containing "gemini" automatically use Gemini provider (e.g., `gemini-2.5-flash-preview-05-20`)
  - Works with mixed case and custom model names
  - Graceful handling of new models before they're added to registry
- **Explicit Provider Parameter**: New `provider` parameter in `call_ai()`
  - Accept AIProvider enum or string values (`'openai'`, `'gemini'`)
  - Overrides automatic model-based inference when specified
  - Useful for custom models or explicit provider control
  - Example: `call_ai(model="custom-model", provider="gemini")`

### 🔧 Improved Error Handling
- **Better Unknown Model Support**: Enhanced fallback behavior for unrecognized models
  - Unknown models now attempt smart provider inference via name patterns
  - Clear error messages for invalid provider specifications
  - Maintains backward compatibility with existing code

### 📚 Enhanced API Flexibility
- **Multiple Ways to Specify Provider**: Users can now control provider selection through:
  1. Model-based automatic inference (existing)
  2. Pattern-based inference for unknown models (new)
  3. Explicit provider parameter (new)
  4. User preference fallback (existing)

## [0.4.3] - 2025-07-19

### 🚀 Major Architecture Refactor
- **Complete Module Reorganization**: Implemented clean separation of concerns across modules
  - `config.py`: Focused on core AI functionality (`call_ai`, client management)
  - `preferences.py`: Dedicated configuration and user preference management
  - `setup.py`: Interactive setup and configuration display utilities
  - `models.py`: Extensible provider and model registry system

### ✨ Enhanced Provider System
- **Registry-Based Architecture**: New `ProviderRegistry` class for extensible provider management
  - Centralized provider configuration (API keys, base URLs, default models)
  - Easy addition of new providers with minimal code changes
  - Self-documenting system showing all capabilities at runtime
- **Smart Provider Inference**: Enhanced `call_ai` with model-first provider detection
  - Automatically detects provider from model name (e.g., `gemini-2.0-flash-lite` → Gemini)
  - Falls back to user preferences when model is unspecified or unknown
  - Works with all registered models across all providers

### ⚡ Performance Improvements
- **Client Caching**: Implemented efficient client caching to avoid recreation
  - Same provider requests reuse cached OpenAI client instances
  - Significant performance improvement for repeated requests
  - Thread-safe client management
- **DRY Principle Implementation**: Eliminated code duplication throughout codebase
  - Removed redundant wrapper functions
  - Extracted reusable utilities for provider/model resolution
  - Cleaner, more maintainable code structure

### 🔧 Developer Experience
- **Better Code Organization**: Clear module responsibilities and cleaner imports
  - Core AI operations isolated from configuration management
  - Interactive setup separated from business logic
  - Registry system makes adding providers trivial
- **Enhanced Type Safety**: Improved type hints and error handling throughout
- **Comprehensive Testing**: All functionality verified after refactoring

### 🔄 Backward Compatibility
- **API Preservation**: All existing functionality and imports preserved
- **Seamless Migration**: No changes required for existing user code
- **Enhanced Functionality**: New capabilities added without breaking changes

## [0.4.2] - 2025-07-19

### Enhanced
- **Improved System Prompt Handling**: Enhanced `call_ai` function for better system prompt control
  - Empty string system prompts (`""`) are now respected instead of using default
  - Prevents duplicate system messages when messages already contain a system message
  - Made `messages` parameter optional - can now use `system_prompt` alone for simple generation
  - Added automatic user message when only system prompt is provided
  - Better handling of edge cases in conversation building

### Added
- **New Test Examples**: Comprehensive test scripts for system prompt functionality
  - `examples/test_system_prompt.py` - Full test suite with all scenarios
  - `examples/simple_system_prompt_test.py` - Quick verification tests
  - Real-world examples like Bhagavad Gita chat implementation

### Documentation
- **Updated API Reference**: Enhanced documentation for `call_ai` with new capabilities
  - Added examples for system-prompt-only usage
  - Documented new optional messages parameter behavior
  - Added comprehensive usage patterns for different scenarios

## [0.4.1] - 2025-07-18 

### Added
- **Advanced API Access**: Exposed `call_ai` function for direct AI requests
  - Full access to unified AI request system with provider switching
  - Built-in response format handling for structured output (JSON)
  - Custom system prompt support with sensible defaults
  - Complete conversation history management
- **Enhanced System Prompts**: Function-specific system prompts for better AI behavior
  - Specialized prompts for summarization, chat, and text generation
  - Default system prompt for consistent AIWand identity
  - Improved response quality and task-specific optimization
- **New Utility Functions**: Additional configuration and inspection utilities
  - `get_ai_client()` - Get configured AI client for current provider
  - `get_current_provider()` - Check currently active provider
  - `get_model_name()` - Get current model name from preferences
  - `DEFAULT_SYSTEM_PROMPT` - Access to default system prompt constant
- **Comprehensive Examples**: New example file `examples/direct_ai_request.py`
  - Demonstrates advanced `call_ai` usage patterns
  - Shows structured output, conversation handling, and model selection
  - Includes best practices for different use cases

### Changed
- **Core Functions**: Updated to use specialized system prompts for better results
- **API Documentation**: Enhanced with advanced functions and comprehensive examples
- **Package Exports**: Organized exports with clear categories (core, config, types, helpers)

## [0.4.0] - 2025-01-27

### Added
- **Latest AI Models**: Support for newest OpenAI and Gemini models
  - OpenAI: `o3`, `o3-mini`, `o1`, `o1-mini`, `gpt-4.1`, `gpt-4.1-mini`
  - Gemini: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-pro`

### Changed
- **Default Models**: Updated to `gpt-4o` (OpenAI) and `gemini-2.0-flash` (Gemini)
- **Documentation**: Updated API reference and CLI docs with latest models

## [0.3.2] - 2025-01-27

### Added
- **Helper Functions**: New utility functions for development and testing
  - `generate_random_number(length=6)` - Generate random numbers with configurable digit length
  - `generate_uuid(version=4, uppercase=False)` - Generate UUIDs (version 1 or 4) with formatting options
- **CLI Helper Commands**: New command-line interface for helper functions
  - `aiwand helper random` - Generate random numbers with `--length` and `--count` options
  - `aiwand helper uuid` - Generate UUIDs with `--version`, `--uppercase`, and `--count` options
- **Enhanced Examples**: Updated `examples/helper_usage.py` with comprehensive helper function demonstrations
- **API Documentation**: Complete documentation for new helper functions in API reference
- **CLI Documentation**: Enhanced CLI reference with helper command examples and usage patterns

### Changed
- **Package Exports**: Added helper functions to public API (`aiwand.generate_random_number`, `aiwand.generate_uuid`)
- **README**: Updated features list and usage examples to showcase helper utilities and CLI commands
- **Documentation**: Enhanced API reference with helper function section and CLI usage patterns
- **CLI Description**: Updated helper command description to emphasize development and testing utilities

### Technical Improvements
- Type-safe random number generation with exact digit length control
- Support for both UUID1 (timestamp-based) and UUID4 (random) generation
- Comprehensive error handling and validation for helper functions
- Added helper utilities to package's `__all__` exports
- CLI integration with batch generation support (multiple numbers/UUIDs)
- Perfect for shell scripting and automation workflows

## [0.3.1] - 2025-01-27

### Fixed
- **Documentation Accuracy**: Removed non-existent `configure_api_key()` function from all documentation
- **API Reference**: Corrected configuration approach to use environment variables and `setup_user_preferences()`
- **Model Names**: Updated supported model lists to match actual implementation
- **Installation Guide**: Fixed programmatic setup examples to show correct methods
- **Package Focus**: Prioritized Python package usage over CLI in documentation

### Changed
- **API Exports**: Removed unrelated Chrome helper functions (`find_chrome_binary`, `get_chrome_version`) from public API
- **Documentation Structure**: Reorganized README to emphasize package-first usage
- **Error Handling**: Enhanced documentation with proper `AIError` exception examples

### Technical Improvements
- Cleaned up package exports to focus on core AI functionality
- Improved documentation consistency across all files
- Better error handling examples and best practices

## [0.3.0] - 2025-06-23

### Added
- **Direct Prompt Support**: New simplified CLI usage - `aiwand "Your prompt here"` for instant AI chat
- **Enhanced CLI Experience**: Direct prompts bypass subcommands for faster interaction
- **Updated Documentation**: Added quick start examples and direct prompt usage guide
- **Backward Compatibility**: All existing subcommands (chat, summarize, generate) continue to work

### Changed
- **CLI Help Text**: Updated to showcase direct prompt feature as primary usage method
- **README Examples**: Prioritized direct prompt usage in documentation
- **CLI Reference**: Added comprehensive direct prompt examples and use cases

### Technical Improvements
- Smart command detection that differentiates between subcommands and direct prompts
- Maintained full backward compatibility with existing CLI structure
- Enhanced argument parsing with better help formatting

## [0.2.0] - 2025-06-23

### Added
- **Interactive Setup System**: New `aiwand setup` command for guided configuration
- **User Preferences**: Persistent configuration storage in `~/.aiwand/config.json`
- **Enhanced Model Support**: Added GPT-4o, GPT-4o-mini, Gemini 2.0 Flash Experimental models
- **Configuration Status Command**: New `aiwand status` to display current settings
- **Smart Provider Selection**: Hierarchical preference system (user config → env vars → auto-detection)
- **Per-Provider Model Selection**: Configure different models for each AI provider
- **AIError Exception Class**: Better error handling with specific error types

### Changed
- **Completely Rewritten Configuration System**: More robust and user-friendly
- **Updated CLI Interface**: Removed old config command, added setup/status commands
- **Enhanced Examples**: Updated to showcase new setup system and preferences
- **Improved Test Suite**: Tests now cover new API functions and error handling
- **Better Error Messages**: More helpful guidance for setup and configuration

### Technical Improvements
- Centralized configuration management with fallback logic
- Support for multiple model options per provider
- Persistent user preference storage
- Enhanced type hints and error handling
- Improved CLI argument parsing and help messages

## [0.1.0] - 2025-06-23

### Added
- Centralized version management (single source of truth in `__init__.py`)
- Comprehensive documentation structure in `docs/` directory
- Professional README with badges and social links  
- X (Twitter) profile integration (@onlyoneaman)
- Detailed installation guide with troubleshooting
- Complete API reference documentation
- CLI reference with examples
- Virtual environment best practices guide

### Changed
- Updated contact email to 2000.aman.sinha@gmail.com
- Streamlined README from 308 to 106 lines (65% reduction)
- Reorganized documentation into modular structure
- Improved package metadata and descriptions

### Fixed
- Improved error handling and validation
- Enhanced setup scripts for development environment

## [0.0.1] - 2025-06-23

### Added
- Initial release of AIWand
- Smart AI provider selection (OpenAI & Gemini APIs)
- Text summarization with multiple styles (concise, detailed, bullet-points)
- AI chat functionality with conversation history support
- Text generation with customizable parameters
- Command line interface (CLI) with auto-model selection
- Virtual environment support with automated setup scripts
- Environment-based configuration with `.env` file support
- Smart model selection based on available API keys
- Support for both OpenAI and Google Gemini models
- Comprehensive error handling and input validation
- MIT License
- PyPI package distribution
- GitHub repository with complete documentation

### Technical Features
- Python 3.8+ compatibility
- Type hints throughout codebase
- Modular architecture with separate config, core, and CLI modules
- Automated development environment setup (Linux/Mac/Windows)
- Professional package structure with src/ layout
- Comprehensive test suite and installation verification 