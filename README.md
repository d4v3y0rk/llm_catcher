# LLM Catcher

LLM Catcher is a Python library that uses Large Language Models to diagnose and explain exceptions in your code.

## Features

- Exception diagnosis using LLMs
- Both synchronous and asynchronous APIs

## Installation

```bash
pip install llm-catcher
```

## Quick Start

1. Create a `.env` file with your OpenAI API key:
```env
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here
```

## Examples

The `examples/` directory contains several examples demonstrating different use cases:

### 1. Minimal Example (`examples/minimal.py`)
- Basic usage with direct LLM exception diagnosis
- Shows how to set up the diagnoser
- Demonstrates basic error handling and diagnosis

### 2. FastAPI Integration (`examples/fastapi_example.py`)
- Shows how to integrate LLM Catcher with FastAPI
- Demonstrates how to handle exceptions in FastAPI
- Includes a Swagger UI endpoint for testing

Run any example like this:
```bash
# Run minimal example
python examples/minimal_example.py

# Run FastAPI example
python examples/fastapi_example.py
# Then visit http://localhost:8000/docs

```

Each example includes detailed comments and demonstrates best practices for using LLM Catcher in different contexts.

## Configuration

All settings can be configured through environment variables or the Settings class:

### Complete Settings Example

```python
from llm_catcher.settings import get_settings

settings = get_settings()

# Required
settings.openai_api_key = "your-api-key"  # Or set via LLM_CATCHER_OPENAI_API_KEY

# Model Settings
settings.llm_model = "gpt-4"  # Options: "gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"
settings.temperature = 0.2  # Range: 0.0-1.0

```

### Environment Variables

The same settings can be configured via environment variables:

```env
# Required
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here

# Model Settings
LLM_CATCHER_LLM_MODEL=gpt-4
LLM_CATCHER_TEMPERATURE=0.2

```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `openai_api_key` | str | None | Your OpenAI API key (required) |
| `llm_model` | str | "gpt-4" | LLM model to use |
| `temperature` | float | 0.2 | Model temperature (0.0-1.0) |

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-catcher.git
cd llm-catcher

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"  # This installs the package with development extras
```

## Notes

- API key is required and must be provided via environment or settings
- Settings are validated on initialization
- Stack traces are included in LLM prompts for better diagnosis

## License

MIT License
