# AIWand 🪄

> **One API to rule them all** - Unified OpenAI and Gemini interface with automatic provider switching and structured data extraction from anywhere.

[![PyPI version](https://img.shields.io/pypi/v/aiwand.svg)](https://pypi.org/project/aiwand/)
[![Python versions](https://img.shields.io/pypi/pyversions/aiwand.svg)](https://pypi.org/project/aiwand/)
[![License](https://img.shields.io/pypi/l/aiwand.svg)](https://github.com/onlyoneaman/aiwand/blob/main/LICENSE)
[![Coverage Status](https://img.shields.io/badge/coverage-100%25-success)](https://github.com/onlyoneaman/aiwand/actions?query=workflow%3ACI)
[![Downloads](https://pepy.tech/badge/aiwand)](https://pepy.tech/project/aiwand)
[![Downloads](https://pepy.tech/badge/aiwand/month)](https://pepy.tech/project/aiwand/month)
[![Downloads](https://pepy.tech/badge/aiwand/week)](https://pepy.tech/project/aiwand/week)

## 🚀 **Stop Wrestling with AI APIs**

**Before:** Different APIs, manual JSON parsing, provider-specific code 😫  
**After:** One API, automatic everything ✨

```python
import aiwand
# Works with any model - provider auto-detected
response = aiwand.call_ai(model="gpt-4o", user_prompt="Explain quantum computing?")

# returns structured json data directly
data = aiwand.extract(content="John Doe, john@example.com, (555) 123-4567")
```

## 🔧 Installation & Setup

```bash
pip install aiwand
export OPENAI_API_KEY="your-key"     # Set either key (or both for fallback)
export GEMINI_API_KEY="your-key"     
```

## 💡 Core Features

### **`call_ai`** - Universal AI Interface
Same code works with OpenAI and Gemini - automatic provider detection:

```python
from pydantic import BaseModel

# Basic AI calls
response = aiwand.call_ai(model="gpt-4o", user_prompt="Explain quantum computing?")

# Structured output - get Pydantic objects directly
class BlogPost(BaseModel):
    title: str
    content: str
    tags: list[str]

blog = aiwand.call_ai(
    model="gemini-2.0-flash",
    user_prompt="Write a blog about AI",
    response_format=BlogPost    # Returns BlogPost object!
)
print(blog.title)  # Direct access, no JSON parsing

# Works with any model
for model in ["gpt-4o", "gemini-2.0-flash", "o3-mini"]:
    response = aiwand.call_ai(model=model, user_prompt=f"What makes {model} special?")
```

### **`extract`** - Smart Data Extraction  
Extract structured data from text, web links, documents, and images:

```python
from pydantic import BaseModel

class CompanyInfo(BaseModel):
    name: str
    founded: int
    employees: int
    technologies: list[str]

# Extract from individual sources
contact = aiwand.extract(content="John Doe, john@example.com, (555) 123-4567")
webpage = aiwand.extract(links=["https://company.com/about"])
docs = aiwand.extract(document_links=["resume.pdf", "report.docx"])
images = aiwand.extract(images=["chart.png", "diagram.jpg"])

# Or mix all sources together with custom structure
company = aiwand.extract(
    content="Research notes about tech companies...", 
    links=["https://company.com/about"],           # Web pages
    document_links=["annual_report.pdf"],          # Documents  
    images=["company_chart.png"],                  # Images
    response_format=CompanyInfo                    # Get typed object back
)

print(f"{company.name} founded in {company.founded}")  # Direct access
```

## ⚡ Quick Examples

```python
import aiwand

# Instant AI calls
summary = aiwand.summarize("Long article...", style="bullet-points")
response = aiwand.chat("What is machine learning?")
story = aiwand.generate_text("Write a haiku about coding")

# Smart classification  
grader = aiwand.create_binary_classifier(criteria="technical accuracy")
result = grader(question="What is 2+2?", answer="4", expected="4")
print(f"Accuracy: {result.score}/5")
```

## 🎨 CLI Magic

```bash
# Quick chat
aiwand "Explain quantum computing simply"

# Extract from anything
aiwand extract "Dr. Sarah Johnson, sarah@lab.com" --json
aiwand extract --links https://example.com --document-links resume.pdf --images chart.png

# Built-in functions
aiwand summarize "Long text..." --style concise
aiwand chat "Hello there!"
```

## ✨ Why Choose AIWand?

| 🔄 **Provider Agnostic** | Same code, OpenAI or Gemini |
|---|---|
| 🏗️ **Structured Output** | Pydantic objects, no JSON parsing |
| 🧠 **Smart Detection** | Automatic provider selection |
| 📄 **Universal Extraction** | Text, web links, documents, images |
| ⚡ **Zero Setup** | Just add API keys |
| 🎯 **Drop-in Ready** | Minimal code changes |

## 📚 Documentation

- **[API Reference](docs/api-reference.md)** - Complete function docs
- **[CLI Guide](docs/cli.md)** - Command line usage  
- **[Installation](docs/installation.md)** - Setup details
- **[Development](docs/development.md)** - Contributing guide

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

⭐ **Star this repo if AIWand makes your AI development easier!**

**Made with ❤️ by [Aman Kumar](https://x.com/onlyoneaman)** 