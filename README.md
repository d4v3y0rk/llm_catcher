[![PyPI Downloads](https://static.pepy.tech/badge/llm-catcher)](https://pepy.tech/projects/llm-catcher)
[![PyPI version](https://badge.fury.io/py/llm-catcher.svg)](https://badge.fury.io/py/llm-catcher)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/d4v3y0rk/llm_catcher/python-package.yml)



# LLM Catcher

Stack traces: the unsung villains of debugging.
Why wrestle with a wall of cryptic error messages when you could let LLM Catcher do the heavy lifting?

LLM Catcher is your debugging sidekick—a Python library that teams up with Large Language Models (Ollama or OpenAI) to decode those pesky exceptions. Instead of copy-pasting a stack trace into your LLM chat and then shuffling back to your IDE, LLM Catcher delivers instant, insightful fixes right in your logs.

Stop debugging the old-fashioned way. Catch the errors, not the headaches!

> ⚠️ **Note**: This project is under active development and may include breaking changes. See [Version Notice](#version-notice) for details.

## Features

- Exception diagnosis using LLMs (Ollama or OpenAI)
- Support for local LLMs through Ollama
- OpenAI integration for cloud-based models
- Multiple error handling approaches:
  - Function decorators for automatic diagnosis
  - Try/except blocks for manual control
  - Global exception handler for unhandled errors from imported modules
- Both synchronous and asynchronous APIs
- Flexible configuration through environment variables or config file

## Installation

1. Install LLM Catcher:
```bash
pip install llm-catcher
```

2. Install Ollama (recommended default setup):

macOS or Windows:
- Download and install from [Ollama.com](https://ollama.com/download)

Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

3. Pull the default model:
```bash
ollama pull qwen2.5-coder
```

That's it! You're ready to use LLM Catcher with the default local setup.

## Quick Start

```python
from llm_catcher import LLMExceptionDiagnoser

# Initialize diagnoser (uses Ollama with qwen2.5-coder by default)
diagnoser = LLMExceptionDiagnoser()

try:
    result = 1 / 0  # This will raise a ZeroDivisionError
except Exception as e:
    diagnosis = diagnoser.diagnose(e)
    print(diagnosis)
```

## Usage Patterns

### Exception Handling Approaches

#### 1. Function Decorator
```python
@diagnoser.catch
def risky_function():
    """Errors will be automatically diagnosed."""
    return 1 / 0

@diagnoser.catch
async def async_risky_function():
    """Works with async functions too."""
    import nonexistent_module
```

#### 2. Try/Except Blocks
```python
# Synchronous
try:
    result = risky_operation()
except Exception as e:
    diagnosis = diagnoser.diagnose(e)
    print(diagnosis)

# Asynchronous
try:
    result = await async_operation()
except Exception as e:
    diagnosis = await diagnoser.async_diagnose(e)
    print(diagnosis)
```

#### 3. Global Exception Handler
By default, LLM Catcher catches all unhandled exceptions. You might want to disable this when:
- You have other error handling middleware or global handlers
- You want to handle exceptions only in specific try/except blocks
- You're using a framework with its own error handling
- You want more control over which exceptions get diagnosed

```python
# Disable global handler for more specific exception handling
diagnoser = LLMExceptionDiagnoser(global_handler=False)
```

### Web Framework Integration

#### FastAPI Example
```python
from fastapi import FastAPI
from llm_catcher import LLMExceptionDiagnoser

app = FastAPI()
diagnoser = LLMExceptionDiagnoser()

@app.get("/error")
async def error():
    try:
        1/0
    except Exception as e:
        diagnosis = await diagnoser.async_diagnose(e, formatted=False)
        return {"error": str(e), "diagnosis": diagnosis}
```

### Formatting Options

The diagnosis output can be formatted in two ways:
- `formatted=True` (default): Returns the diagnosis with clear formatting and boundaries
- `formatted=False`: Returns plain text, suitable for JSON responses

### Debug Mode

For detailed diagnostic information:
```bash
DEBUG=true python your_script.py
```

[Configuration section follows...]

## Configuration

LLM Catcher can be configured in multiple ways, with the following precedence (highest to lowest):

1. Local config files:
   - `./llm_catcher_config.json`
   - `./config.json`
2. User home config:
   - `~/.llm_catcher_config.json`
3. Environment variables
4. Default values

### Config Files

Create a JSON config file in your project or home directory:

```json
{
    "provider": "openai",
    "llm_model": "gpt-4",
    "temperature": 0.2,  # Only used with OpenAI
    "openai_api_key": "sk-your-api-key"
}
```

### Environment Variables

Environment variables can be set directly or through a `.env` file:

```bash
# Required for OpenAI provider
LLM_CATCHER_OPENAI_API_KEY=sk-your-api-key

# Optional settings
LLM_CATCHER_PROVIDER=openai     # or 'ollama'
LLM_CATCHER_LLM_MODEL=gpt-4    # or any supported model
LLM_CATCHER_TEMPERATURE=0.2    # Only used with OpenAI
```

## Supported Models

### Default Setup (Ollama)
- `qwen2.5-coder` (default): Optimized for code understanding and debugging
- Any other Ollama model can be used

### OpenAI Models

GPT-4o Series (Recommended):
- `gpt-4o`: Advanced multimodal model with superior reasoning capabilities
- `gpt-4o-mini`: Cost-effective version with excellent performance

o1 Series (Recommended for Complex Code):
- `o1`: Specialized for coding, science, and mathematical reasoning
- `o1-mini`: Faster variant with similar capabilities

GPT-4 Series:
- `gpt-4` (default for OpenAI): Strong general-purpose model
- `gpt-4-turbo`: Latest version with improved performance

GPT-3.5 Series (Economy Option):
- `gpt-3.5-turbo`: Good balance of performance and cost
- `gpt-3.5-turbo-16k`: Extended context version for longer stack traces

Note: When using OpenAI, if no model is specified, `gpt-4` will be used as the default.

## Examples

The `examples/` directory contains several examples demonstrating different use cases:

- `minimal_example.py`: Basic usage with try/except and global handler
- `decorator_example.py`: Using the function decorator with both sync and async functions
- `fastapi_example.py`: Integration with FastAPI

Check out these examples to see LLM Catcher in action with different patterns and frameworks.

### Debug Mode

Set the `DEBUG` environment variable to see detailed diagnostic information:
```bash
DEBUG=true python your_script.py
```

## Notes

- Ollama must be installed and running for local LLM support (default)
- OpenAI API key is required only when using OpenAI provider
- Settings are validated on initialization
- Stack traces are included in LLM prompts for better diagnosis

## Version Notice

⚠️ **Pre-1.0.0 Version Notice**: This project is in active development and may introduce breaking changes between versions. Notable changes include:

- Changed default provider from OpenAI to Ollama
- Added global exception handler (enabled by default)
- Added function decorator support

If you're upgrading from an earlier version, please review these changes. We recommend pinning to a specific version in your dependencies until we reach 1.0.0:

```bash
pip install llm-catcher==0.3.5
```

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for more details.

## Development

### Testing

Run the test suite:
```bash
./scripts/test.sh
```

### Linting

Check code style:
```bash
./scripts/lint.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more detailed development instructions.
