# LLM Catcher

A Python library that uses LLMs to diagnose and explain exceptions in real-time.

## Installation

```bash
pip install llm-catcher
```

## Quick Start

1. Create a `.env` file with your OpenAI API key:
```env
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here
```

2. Configure exception handling:
```env
# Choose one of these modes:
LLM_CATCHER_HANDLED_EXCEPTIONS=UNHANDLED  # Only handle uncaught exceptions (default)
LLM_CATCHER_HANDLED_EXCEPTIONS=ALL        # Handle all exceptions

# Or specify exact exceptions to handle:
LLM_CATCHER_HANDLED_EXCEPTIONS=ValueError,TypeError,ValidationError
```

## Configuration

All settings can be configured through environment variables or passed directly to the Settings class.

### Required Settings

- `LLM_CATCHER_OPENAI_API_KEY`: Your OpenAI API key (required)

### Optional Settings

- `LLM_CATCHER_LLM_MODEL`: Model to use (default: "gpt-4")
  - Supported models: "gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"
- `LLM_CATCHER_TEMPERATURE`: Model temperature (default: 0.2, range: 0-1)

### Exception Handling

Configure which exceptions to handle:
```env
# Use UNHANDLED mode (default)
LLM_CATCHER_HANDLED_EXCEPTIONS=UNHANDLED

# Use ALL mode
LLM_CATCHER_HANDLED_EXCEPTIONS=ALL

# Handle specific exceptions (comma-separated)
LLM_CATCHER_HANDLED_EXCEPTIONS=ValueError,TypeError,ValidationError
```

### Ignoring Exceptions

Specify exceptions to ignore (these take precedence over handled exceptions):
```env
# Comma-separated list (default: KeyboardInterrupt,SystemExit)
LLM_CATCHER_IGNORE_EXCEPTIONS=KeyboardInterrupt,SystemExit
```

### Custom Prompts

Add custom prompts for specific exception types:
```env
# JSON format for custom handlers
LLM_CATCHER_CUSTOM_HANDLERS={
    "ValueError": "Please analyze this value error and provide: 1) The exact location, 2) The cause, 3) How to fix it",
    "TypeError": "Explain this type error and suggest fixes"
}
```

## Environment Variables vs Direct Configuration

You can configure LLM Catcher either through environment variables or by passing settings directly:

```python
from llm_catcher import Settings

# Using environment variables (recommended)
settings = Settings()

# Or passing settings directly
settings = Settings(
    openai_api_key="your-api-key",
    handled_exceptions=["ValueError", "TypeError"],
    ignore_exceptions=["KeyboardInterrupt"],
    custom_handlers={"ValueError": "Custom prompt"},
    llm_model="gpt-4",
    temperature=0.5
)
```

## Example Usage

### FastAPI Integration

```python
from fastapi import FastAPI
from llm_catcher.middleware import LLMCatcherMiddleware

app = FastAPI()

# Add the middleware
app.add_middleware(LLMCatcherMiddleware)
```

### CLI Application

```python
from llm_catcher import LLMExceptionDiagnoser

# Initialize the diagnoser
diagnoser = LLMExceptionDiagnoser()

try:
    # Your code here
    result = 1 / 0
except Exception as e:
    # Get AI-powered diagnosis
    diagnosis = await diagnoser.diagnose(e)
    print(diagnosis)
```

## Notes

- The OpenAI API key is required and must be provided either through environment variables or direct configuration
- Settings are validated on initialization
- Invalid values will fall back to defaults
- Environment variables take precedence over direct configuration
- Custom handlers must be valid JSON when provided through environment variables