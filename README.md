# LLM Catcher

LLM Catcher is a Python library that uses Large Language Models to diagnose and explain exceptions in your code.

## Features

- Automatic exception diagnosis using LLMs
- FastAPI middleware for handling API exceptions
- Customizable exception handling
- Support for custom prompts per exception type
- Configurable via environment variables or code

## Installation

```bash
pip install llm-catcher
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

## Examples

The `examples/` directory contains several examples demonstrating different use cases:

### 1. Minimal Example (`examples/minimal.py`)
- Basic usage with direct LLM exception diagnosis
- Shows how to set up the diagnoser
- Demonstrates basic error handling and diagnosis

### 2. FastAPI Integration (`examples/fastapi_example.py`)
- Shows FastAPI middleware integration
- Demonstrates custom error handlers
- Includes Pydantic schema validation
- Shows different error scenarios
- Includes custom prompts for specific errors

### 3. CLI Example (`examples/cli_example.py`)
- Demonstrates both UNHANDLED and ALL modes
- Shows difference between caught and uncaught exceptions
- Shows standard error handling vs LLM diagnosis
- Includes stack trace handling

Run any example like this:
```bash
# Run minimal example
python examples/minimal.py

# Run FastAPI example
python examples/fastapi_example.py
# Then visit http://localhost:8000/docs

# Run CLI example
python examples/cli_example.py
```

Each example includes detailed comments and demonstrates best practices for using LLM Catcher in different contexts.

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

MIT License