# API Reference

Complete documentation for all AIWand functions and features.

## Core Functions

### `summarize(text, max_length=None, style="concise", model=None)`

Summarize text with customizable options.

**Parameters:**
- `text` (str): Text to summarize
- `max_length` (int, optional): Maximum words in summary
- `style` (str): Summary style - "concise", "detailed", or "bullet-points"
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Summarized text (str)

**Raises:**
- `ValueError`: If text is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Basic summarization
summary = aiwand.summarize("Your long text here...")

# Customized summarization
summary = aiwand.summarize(
    text="Your text...",
    style="bullet-points",
    max_length=50,
    model="gpt-4"
)
```

### `chat(message, conversation_history=None, model=None, temperature=0.7)`

Have a conversation with AI.

**Parameters:**
- `message` (str): Your message
- `conversation_history` (list, optional): Previous conversation messages
- `model` (str, optional): Specific model to use (auto-selected if not provided)
- `temperature` (float): Response creativity (0.0-1.0)

**Returns:** AI response (str)

**Raises:**
- `ValueError`: If message is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Simple chat
response = aiwand.chat("What is machine learning?")

# Conversation with history
conversation = []
response1 = aiwand.chat("Hello!", conversation_history=conversation)
conversation.append({"role": "user", "content": "Hello!"})
conversation.append({"role": "assistant", "content": response1})

response2 = aiwand.chat("What did I just say?", conversation_history=conversation)
```

### `generate_text(prompt, max_output_tokens=500, temperature=0.7, model=None)`

Generate text from a prompt.

**Parameters:**
- `prompt` (str): Text prompt
- `max_output_tokens` (int): Maximum tokens to generate
- `temperature` (float): Response creativity (0.0-1.0)
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Generated text (str)

**Raises:**
- `ValueError`: If prompt is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Basic generation
text = aiwand.generate_text("Write a poem about coding")

# Customized generation
text = aiwand.generate_text(
    prompt="Write a technical explanation of neural networks",
    max_output_tokens=300,
    temperature=0.3,
    model="gpt-4"
)
```

### `extract(content=None, links=None, model=None, temperature=0.7, response_format=None)`

Extract structured data from content and/or links using AI.

**Parameters:**
- `content` (Union[str, Any], optional): Any content to extract from - will be converted to string. Can be str, dict, list, or any object with __str__ method.
- `links` (List[str], optional): List of URLs or file paths to fetch and include in extraction. URLs (http/https) will be fetched, file paths will be read.
- `model` (str, optional): Specific AI model to use (auto-selected if not provided)
- `temperature` (float): Response creativity (0.0-1.0, default 0.7)
- `response_format` (BaseModel, optional): Pydantic model class for structured output

**Returns:** Union[str, Dict[str, Any]]: Extracted data. Dict if JSON parsing succeeds, formatted string otherwise.

**Raises:**
- `ValueError`: If neither content nor links are provided
- `AIError`: If the AI call fails
- `FileNotFoundError`: If file path doesn't exist

**Example:**
```python
import aiwand
from pydantic import BaseModel

# Simple text extraction
result = aiwand.extract(content="John Doe, email: john@example.com")

# Extract from URLs
result = aiwand.extract(links=["https://example.com/article"])

# Mix content and links with structured output
class ContactInfo(BaseModel):
    name: str
    email: str

result = aiwand.extract(
    content="Meeting notes: contact John at john@example.com",
    links=["https://company.com/about", "/path/to/business_card.txt"],
    response_format=ContactInfo
)

# Complex content (dict/list converted to string)
data = {"name": "John", "email": "john@example.com"}
result = aiwand.extract(content=data)
```

## Helper Functions

### `generate_random_number(length=6)`

Generate a random number with specified number of digits.

**Parameters:**
- `length` (int): Number of digits for the random number (default: 6)

**Returns:** Random number as string (preserves leading zeros)

**Raises:**
- `ValueError`: If length is less than 1

**Example:**
```python
import aiwand

# Default 6-digit number
number = aiwand.generate_random_number()
print(f"6-digit: {number}")  # e.g., "432875"

# Custom length
number = aiwand.generate_random_number(10)
print(f"10-digit: {number}")  # e.g., "9847382659"

# Single digit
number = aiwand.generate_random_number(1)
print(f"1-digit: {number}")  # e.g., "7"
```

### `generate_uuid(version=4, uppercase=False)`

Generate a UUID (Universally Unique Identifier).

**Parameters:**
- `version` (int): UUID version to generate (1 or 4, default: 4)
- `uppercase` (bool): Whether to return uppercase UUID (default: False)

**Returns:** Generated UUID string

**Raises:**
- `ValueError`: If version is not 1 or 4

**Example:**
```python
import aiwand

# Default UUID4
uuid = aiwand.generate_uuid()
print(f"UUID4: {uuid}")  # e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479"

# UUID4 uppercase
uuid = aiwand.generate_uuid(uppercase=True)
print(f"UUID4: {uuid}")  # e.g., "F47AC10B-58CC-4372-A567-0E02B2C3D479"

# UUID1 (includes timestamp and MAC address)
uuid = aiwand.generate_uuid(version=1)
print(f"UUID1: {uuid}")  # e.g., "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
```

## Advanced Functions

### `call_ai(messages=None, max_output_tokens=None, temperature=0.7, top_p=1.0, model=None, provider=None, response_format=None, system_prompt=None, user_prompt=None, additional_system_instructions=None, images=None)`

Low-level unified AI request function with automatic provider switching and advanced features.

**Parameters:**
- `messages` (list, optional): List of message dictionaries with 'role' and 'content'. If None or empty, a default user message will be added.
- `max_output_tokens` (int, optional): Maximum tokens to generate
- `temperature` (float): Response creativity (0.0-1.0, default: 0.7)
- `top_p` (float): Nucleus sampling parameter (0.0-1.0, default: 1.0)
- `model` (str/enum, optional): Specific model to use (auto-selected if not provided)
- `provider` (str/enum, optional): AI provider to use explicitly ('openai', 'gemini', or AIProvider enum). Overrides model-based inference.
- `response_format` (dict, optional): Response format specification (e.g., {"type": "json_object"})
- `system_prompt` (str, optional): Custom system prompt (uses default if None)
- `user_prompt` (str, optional): User message to append to the messages list. Can be used with or without existing messages.
- `additional_system_instructions` (str, optional): Additional instructions to append to the system prompt. If provided, will be added to the end of the system message with proper spacing.
- `images` (list, optional): List of images to add to the messages list. Can be a list of strings (URLs), Path objects, or bytes.
- `document_links` (list, optional): List of URLs to fetch and include in the messages list.
- `reasoning_effort` (str, optional): Reasoning effort for Gemini models. Can be "low", "medium", or "high".
- `tool_choice` (str, optional): Tool choice for OpenAI models. Can be "auto", "none", or "required".
- `tools` (list, optional): List of tools to use for the AI call. Can be a list of tool dictionaries with 'type', 'function', and 'description'.
- `use_google_search` (bool, optional): Whether to use the Google search tool for Gemini models. Only works with Gemini models.

**Returns:** AI response content (str)

**Raises:**
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Basic request
messages = [{"role": "user", "content": "Explain quantum computing"}]
response = aiwand.call_ai(messages)

# Advanced request with all options
response = aiwand.call_ai(
    system_prompt="You are a data scientist. Provide structured analysis.",
    user_prompt="Analyze this data",
    response_format={"type": "json_object"},
    temperature=0.3,
    model=aiwand.OpenAIModel.GPT_4O,
    provider="openai",
    max_output_tokens=500
)

# Using user_prompt to extend existing conversation
conversation = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."}
]
response = aiwand.call_ai(
    messages=conversation,
    user_prompt="How do I install it?",  # Adds this as new user message
    system_prompt="You are a helpful programming tutor."
)

# Conversation with history
conversation = [
    {"role": "user", "content": "Hi, I'm learning Python."},
    {"role": "assistant", "content": "Great! Python is an excellent language..."},
    {"role": "user", "content": "What should I learn first?"}
]
response = aiwand.call_ai(
    messages=conversation,
    system_prompt="You are a patient programming tutor."
)

# Building conversation history with system message in messages array
system_prompt = """
You are Bhagavad Gita speaking timeless wisdom.
Respond to queries with spiritual insight, calmness, clarity, and references to Gita teachings when relevant.
Use a tone that is gentle, uplifting, and philosophical.
Drive the conversation try to find more about the user, keep it like a conversation and guide user.
Avoid being overly verbose or technical. Keep messages short.
"""

# Build history from previous conversation (e.g., from database)
history = []
# Simulate loading from database: messages = Message.get_by_thread_id(thread_id)
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

response = aiwand.call_ai(
    model="gemini-2.0-flash",
    messages=model_messages
)

# Simple generation using only system prompt (no messages needed)
response = aiwand.call_ai(
    system_prompt="You are a creative writer. Write a short story about a time traveler.",
    temperature=0.8,
    max_output_tokens=200
)

# Empty messages with system prompt
response = aiwand.call_ai(
    messages=[],
    system_prompt="Generate 3 programming tips for beginners.",
    temperature=0.5
)

# Using additional_system_instructions to extend system prompt
response = aiwand.call_ai(
    system_prompt="You are a helpful programming tutor.",
    additional_system_instructions="Always provide code examples and explain each step clearly.",
    user_prompt="How do I create a Python class?"
)

# Adding context-specific instructions to existing conversation
conversation = [
    {"role": "user", "content": "I'm learning data science"},
    {"role": "assistant", "content": "Great! Data science combines statistics, programming, and domain expertise..."}
]
response = aiwand.call_ai(
    messages=conversation,
    user_prompt="What should I learn next?",
    additional_system_instructions="Focus on practical, hands-on learning resources and provide specific next steps."
)

# Extending default system prompt with specialized instructions
response = aiwand.call_ai(
    user_prompt="Write a function to calculate fibonacci numbers",
    additional_system_instructions="Write clean, well-documented code with error handling and include unit tests."
)
```

### `get_ai_client()`

Get configured AI client for the current provider.

**Returns:** OpenAI client configured for current provider

**Raises:**
- `AIError`: When no API provider is available

### `get_current_provider()`

Get the currently active AI provider.

**Returns:** AIProvider enum (OPENAI or GEMINI) or None

### `get_model_name()`

Get the model name for the current provider based on user preferences.

**Returns:** Model name string

**Raises:**
- `AIError`: When no provider is available

### `DEFAULT_SYSTEM_PROMPT`

Default system prompt used when none is specified.

**Value:** `"You are AIWand, a helpful AI assistant that provides clear, accurate, and concise responses. You excel at text processing, analysis, and generation tasks."`

**Example:**
```python
import aiwand

# Check current default
print(aiwand.DEFAULT_SYSTEM_PROMPT)

# Use in custom request
response = aiwand.call_ai(
    messages=[{"role": "user", "content": "Hello"}],
    system_prompt=aiwand.DEFAULT_SYSTEM_PROMPT
)
```

## Configuration Functions

### `setup_user_preferences()`

Interactive setup for user preferences (provider and model selection).

**Parameters:** None

**Returns:** None

**Example:**
```python
import aiwand

# Run interactive setup
aiwand.setup_user_preferences()
```

### `show_current_config()`

Display current configuration and available providers.

**Parameters:** None

**Returns:** None

**Example:**
```python
import aiwand

# Show current configuration
aiwand.show_current_config()
```

## Configuration

AIWand uses environment variables for configuration:

```bash
# Required: At least one API key
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# Optional: Default provider when both keys available
export AI_DEFAULT_PROVIDER="openai"  # or "gemini"
```

## Smart Model Selection

AIWand automatically selects the best available model:

| Available APIs | Default Model | Provider |
|----------------|---------------|----------|
| OpenAI only | `gpt-4o` | OpenAI |
| Gemini only | `gemini-2.0-flash` | Gemini |
| Both available | Based on `AI_DEFAULT_PROVIDER` or preferences | Configurable |

### Supported Models

**OpenAI Models:**
- `o3` (newest reasoning model, best performance)
- `o3-mini` (efficient reasoning model)
- `o1` (advanced reasoning model)
- `o1-mini` (compact reasoning model)
- `gpt-4.1` (1M context window, best for coding)
- `gpt-4.1-mini` (efficient large context model)
- `gpt-4o` (default - multimodal flagship)
- `gpt-4o-mini` (fast, capable, cost-effective)
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

**Gemini Models:**
- `gemini-2.5-pro` (newest flagship model)
- `gemini-2.5-flash` (latest experimental model)
- `gemini-2.5-flash-lite` (efficient variant)
- `gemini-2.0-flash-exp` (experimental features)
- `gemini-2.0-flash` (default - stable, fast, capable)
- `gemini-2.0-pro`
- `gemini-1.5-flash`
- `gemini-1.5-pro`

## Error Handling

### AIError

Custom exception for AI-related errors.

**Common scenarios:**
- No API keys configured
- API call failures
- Network issues
- Provider-specific errors

**Example:**
```python
import aiwand

try:
    summary = aiwand.summarize("Some text")
except aiwand.AIError as e:
    print(f"AI service error: {e}")
    # Handle API issues, missing keys, etc.
except ValueError as e:
    print(f"Input error: {e}")
    # Handle empty text, invalid parameters, etc.
```

## Best Practices

### Environment Setup
```python
# Use environment variables or .env file
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# AIWand will automatically pick up the keys
import aiwand
```

### Error Handling
```python
import aiwand

def safe_summarize(text):
    try:
        return aiwand.summarize(text)
    except aiwand.AIError as e:
        print(f"AI service unavailable: {e}")
        return None
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
```

### Model Selection
```python
import aiwand

# Let AIWand choose the best model
response = aiwand.chat("Hello")

# Or specify a model for specific needs
creative_response = aiwand.generate_text(
    "Write a creative story",
    model="gpt-4",
    temperature=0.9
)

factual_response = aiwand.generate_text(
    "Explain quantum physics",
    model="gpt-4",
    temperature=0.2
)
```

### Using Helper Functions
```python
import aiwand

# Generate random data for testing
test_id = aiwand.generate_random_number(8)
session_id = aiwand.generate_uuid()

# Create unique identifiers
user_id = f"user_{aiwand.generate_random_number(6)}"
transaction_id = aiwand.generate_uuid(uppercase=True)

print(f"Test ID: {test_id}")
print(f"Session: {session_id}")
print(f"User: {user_id}")
print(f"Transaction: {transaction_id}")
``` 