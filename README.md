# LLM Catcher

A Python library that uses LLMs to diagnose and explain exceptions in real-time. It provides intelligent error diagnosis for Python applications, with special support for FastAPI.

## Features

- Intelligent exception diagnosis using OpenAI's GPT models
- FastAPI middleware for automatic error handling
- Support for both caught and uncaught exceptions
- Custom error handlers and prompts
- Environment-based configuration
- Comprehensive stack trace analysis
- Schema-aware error diagnosis for FastAPI

## Installation

```bash
# Install from PyPI
pip install llm-catcher

# For development
pip install llm-catcher[dev]
```

## Quick Start

1. Create a `.env` file with your OpenAI API key:
```env
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here
```

2. Choose your exception handling mode:
```env
# Only handle uncaught exceptions (default)
LLM_CATCHER_HANDLED_EXCEPTIONS=UNHANDLED

# Or handle all exceptions
LLM_CATCHER_HANDLED_EXCEPTIONS=ALL

# Or specify exact exceptions
LLM_CATCHER_HANDLED_EXCEPTIONS=ValueError,TypeError,ValidationError
```

## Minimal Example

```python
import asyncio
from llm_catcher import LLMExceptionDiagnoser

async def main():
    diagnoser = LLMExceptionDiagnoser()
    try:
        1/0  # Cause an error
    except Exception as e:
        print(await diagnoser.diagnose(e))

if __name__ == "__main__":
    asyncio.run(main())
```

## FastAPI Integration

```python
from fastapi import FastAPI
from llm_catcher.middleware import LLMCatcherMiddleware
from llm_catcher.settings import Settings

app = FastAPI()

# Configure with Settings object
settings = Settings(
    handled_exceptions=["UNHANDLED"],  # Only handle uncaught exceptions
    ignore_exceptions=["KeyboardInterrupt"],
    custom_handlers={
        "ValueError": "This is a validation error. Please check: \n1. Input types\n2. Required fields",
        "ZeroDivisionError": "This is a division by zero error. Check division operations."
    }
)

# Add the middleware
app.add_middleware(LLMCatcherMiddleware, settings=settings)

# Custom handler for specific exceptions (respected in UNHANDLED mode)
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": "Custom handler: Invalid value provided"}
    )
```

## Standalone Usage

```python
import asyncio
from llm_catcher import LLMExceptionDiagnoser
import traceback

async def main():
    # Initialize diagnoser
    diagnoser = LLMExceptionDiagnoser()

    try:
        # Your code here
        result = 1 / 0
    except Exception as e:
        # Get full stack trace
        stack_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        # Get AI-powered diagnosis
        diagnosis = await diagnoser.diagnose(stack_trace)
        print(diagnosis)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

All settings can be configured through environment variables or the Settings class:

### Required Settings

- `LLM_CATCHER_OPENAI_API_KEY`: Your OpenAI API key

### Optional Settings

- `LLM_CATCHER_LLM_MODEL`: Model to use (default: "gpt-4")
  - Supported: "gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"
- `LLM_CATCHER_TEMPERATURE`: Model temperature (default: 0.2, range: 0-1)
- `LLM_CATCHER_HANDLED_EXCEPTIONS`: Which exceptions to handle
- `LLM_CATCHER_IGNORE_EXCEPTIONS`: Exceptions to ignore
- `LLM_CATCHER_CUSTOM_HANDLERS`: Custom prompts for specific exceptions

## Exception Handling Modes

### UNHANDLED Mode (Default)
```env
LLM_CATCHER_HANDLED_EXCEPTIONS=UNHANDLED
```
- Only handles exceptions that aren't caught by other handlers
- Respects existing exception handlers
- Perfect for adding AI diagnosis without disrupting existing error handling

### ALL Mode
```env
LLM_CATCHER_HANDLED_EXCEPTIONS=ALL
```
- Handles all exceptions (except those in ignore_exceptions)
- Provides AI diagnosis even for caught exceptions
- Useful when you want AI diagnosis for every error

### Specific Exceptions
```env
LLM_CATCHER_HANDLED_EXCEPTIONS=ValueError,TypeError,ValidationError
```
- Only handles listed exception types
- Can be combined with custom handlers

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
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=llm_catcher

# Run specific test file
pytest tests/test_settings.py -v
```

### Examples

The `examples/` directory contains two examples demonstrating different use cases:

1. **CLI Example** (`cli_example.py`):
   - Demonstrates both UNHANDLED and ALL modes
   - Shows difference between caught and uncaught exceptions
   - Shows standard error handling vs LLM diagnosis
   - Includes stack trace handling
   ```bash
   # Run CLI example
   python examples/cli_example.py
   ```

2. **FastAPI Example** (`fastapi_example.py`):
   - Shows FastAPI middleware integration
   - Demonstrates custom error handlers
   - Includes Pydantic schema validation
   - Shows different error scenarios and their handling
   - Includes custom prompts for specific errors
   ```bash
   # Run FastAPI example
   python examples/fastapi_example.py
   # Then test with curl or browser at http://localhost:8000/docs
   ```

Each example includes detailed comments and demonstrates best practices for using LLM Catcher in different contexts. The FastAPI example also includes Swagger documentation accessible through the `/docs` endpoint.

## Notes

- API key is required and must be provided via environment or settings
- Settings are validated on initialization
- Invalid values fall back to defaults
- Environment variables take precedence over direct configuration
- Custom handlers must be valid JSON when provided via environment
- Stack traces are included in LLM prompts for better diagnosis

## License

This project is licensed under the MIT License - see the LICENSE file for details.