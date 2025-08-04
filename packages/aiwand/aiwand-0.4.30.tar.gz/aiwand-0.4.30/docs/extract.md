# AIWand Extract Functionality

The `extract` functionality in AIWand allows you to extract structured data from various types of content including text, files, and URLs. This powerful feature uses **deterministic input specifications** to ensure reliable processing and supports multiple inputs for comprehensive data extraction.

## 🎯 Key Improvements (New)

- **Deterministic Input Handling**: No more guessing - explicitly specify input types
- **Multiple Inputs**: Process text, files, and URLs together in a single extraction
- **Type Safety**: Use `ExtractInput` objects for validation and clarity
- **Better Error Prevention**: Clear error messages and validation
- **Backward Compatibility**: Simple string inputs still work

## Overview

- **Input Types**: Direct text, file paths, URLs - explicitly specified
- **Multiple Inputs**: Combine different sources in one extraction
- **Output Formats**: Free-form structured text or validated Pydantic models
- **Extraction Types**: Configurable hints for what type of data to extract
- **Extensible**: Support for custom Pydantic models

## Basic Usage

### Python API

```python
import aiwand

# Basic extraction
result = aiwand.extract("John Doe, email: john@example.com, phone: 555-1234")
print(result)

# Extract with format hint
result = aiwand.extract(text, extraction_type="contact_info")

# Extract with predefined model
result = aiwand.extract(text, response_format=aiwand.ContactInfo)
print(result)  # Returns a dictionary
```

### Command Line Interface

```bash
# Basic extraction from text
aiwand extract "John Doe, email: john@example.com, phone: 555-1234"

# Extract from file
aiwand extract document.txt --format contact

# Extract from URL
aiwand extract https://example.com/article --format news --json

# Extract with custom type hint
aiwand extract data.txt --type "financial_metrics"
```

## Input Types

The extract function automatically detects the input type:

### 1. Direct Text
```python
text = "Dr. Sarah Johnson, CTO at TechCorp..."
result = aiwand.extract(text)
```

### 2. File Paths
```python
# Automatically reads file content
result = aiwand.extract("/path/to/document.txt")
```

### 3. URLs
```python
# Automatically fetches web content
result = aiwand.extract("https://example.com/article")
```

## Predefined Models

AIWand includes several predefined Pydantic models for common extraction tasks:

### Available Models

| Model Name | Use Case | CLI Format |
|------------|----------|------------|
| `ContactInfo` | Contact information | `contact` |
| `EventInfo` | Event details | `event` |
| `PersonEntity` | Person entities | `person` |
| `OrganizationEntity` | Organizations | `organization` |
| `FinancialData` | Financial information | `financial` |
| `KeyPoints` | Key points/summaries | `keypoints` |
| `ProductInfo` | Product details | `product` |
| `NewsArticleData` | News articles | `news` |
| `DocumentStructure` | Document metadata | `document` |
| `MeetingNotes` | Meeting information | `meeting` |

### Example: Contact Information

```python
from aiwand import extract, ContactInfo

text = """
Dr. Sarah Johnson
Chief Technology Officer
InnovateLabs Inc.
Email: sarah.johnson@innovatelabs.com
Phone: +1 (415) 555-0123
"""

result = extract(text, response_format=ContactInfo)
# Returns:
# {
#   "name": "Dr. Sarah Johnson",
#   "email": "sarah.johnson@innovatelabs.com",
#   "phone": "+1 (415) 555-0123",
#   "company": "InnovateLabs Inc.",
#   "title": "Chief Technology Officer",
#   "address": null,
#   "website": null
# }
```

## Custom Models

Create your own Pydantic models for specific extraction needs:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class RecipeInfo(BaseModel):
    """Custom model for recipe extraction."""
    name: str = Field(..., description="Recipe name")
    prep_time: Optional[str] = Field(None, description="Preparation time")
    ingredients: List[str] = Field(default_factory=list, description="Ingredients")
    instructions: List[str] = Field(default_factory=list, description="Instructions")

# Use your custom model
result = extract(recipe_text, response_format=RecipeInfo)
```

## Function Parameters

```python
def extract(
    content: str,
    response_format: Optional[Type[BaseModel]] = None,
    extraction_type: Optional[str] = None,
    model: Optional[ModelType] = None,
    temperature: float = 0.1
) -> Union[str, Dict[str, Any]]:
```

### Parameters

- **`content`**: Input content (text, file path, or URL)
- **`response_format`**: Pydantic model class for structured output
- **`extraction_type`**: Hint for extraction focus (e.g., "contact_info", "financial_data")
- **`model`**: Specific AI model to use (auto-selected if not provided)
- **`temperature`**: Response creativity (0.0-1.0, default 0.1 for consistency)

### Return Values

- **With `response_format`**: Dictionary conforming to the Pydantic model
- **Without `response_format`**: Formatted string with extracted data

## CLI Options

```bash
aiwand extract [content] [options]
```

### Options

- `--format`: Predefined format (`contact`, `event`, `news`, etc.)
- `--type`: Extraction type hint
- `--model`: AI model to use
- `--temperature`: Response creativity (0.0-1.0)
- `--json`: Force JSON output

### Examples

```bash
# Extract contact info in JSON format
aiwand extract "John Doe, john@example.com" --format contact

# Extract from file with type hint
aiwand extract document.pdf --type "key_points" --json

# Extract from URL with specific model
aiwand extract https://news.example.com/article --format news --model gpt-4
```

## Advanced Usage

### Multiple Extraction Types

```python
# Extract different types from the same content
text = "Meeting with John Doe (john@example.com) on March 15, 2024"

contacts = extract(text, response_format=ContactInfo)
events = extract(text, response_format=EventInfo)
```

### Error Handling

```python
from aiwand import extract, AIError

try:
    result = extract(content, response_format=ContactInfo)
except FileNotFoundError:
    print("File not found")
except AIError as e:
    print(f"AI processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Custom Extraction Types

```python
# Use descriptive extraction types for better results
result = extract(text, extraction_type="financial_metrics_with_percentages")
result = extract(text, extraction_type="technical_specifications")
result = extract(text, extraction_type="contact_information_including_social_media")
```

## Best Practices

### 1. Choose Appropriate Models
- Use predefined models when they fit your use case
- Create custom models for specific domain needs
- Include helpful field descriptions in custom models

### 2. Optimize Extraction Types
- Be specific with extraction type hints
- Use descriptive language that guides the AI
- Combine multiple extraction calls for complex data

### 3. Handle Different Input Types
- Validate file paths exist before extraction
- Handle network timeouts for URL content
- Consider file size limitations for large documents

### 4. Error Handling
- Always wrap extraction calls in try-catch blocks
- Handle specific exceptions (FileNotFoundError, AIError)
- Provide fallback behavior for failed extractions

## Examples

See `examples/extract_usage.py` for comprehensive examples including:
- Basic text extraction
- Contact information extraction
- Event details extraction
- Custom model creation
- File and URL processing
- Error handling patterns

## Model Registry

Access all predefined models programmatically:

```python
from aiwand import EXTRACTION_MODELS

# List available models
for name, model_class in EXTRACTION_MODELS.items():
    print(f"{name}: {model_class.__doc__}")

# Use models dynamically
model_class = EXTRACTION_MODELS["contact"]
result = extract(text, response_format=model_class)
```

## Integration with Other AIWand Features

The extract functionality integrates seamlessly with other AIWand features:

```python
import aiwand

# Extract key points, then summarize them
key_points = aiwand.extract(document, response_format=aiwand.KeyPoints)
summary = aiwand.summarize(key_points["summary"])

# Extract contact info, then generate follow-up email
contact = aiwand.extract(text, response_format=aiwand.ContactInfo)
email = aiwand.generate_text(f"Write a follow-up email to {contact['name']}")
``` 