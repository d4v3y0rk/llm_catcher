# LLM Catcher

LLM Catcher is a Python library that uses Large Language Models to diagnose and explain exceptions in your code.

## Features

- Exception diagnosis using LLMs (OpenAI or Ollama)
- Both synchronous and asynchronous APIs
- Support for local LLMs through Ollama
- Flexible configuration through environment variables or config file

## Installation

```bash
pip install llm-catcher
```

## Quick Start

You can use LLM Catcher with either OpenAI's API or local models through Ollama.

### Using OpenAI

1. Create a `.env` file with your OpenAI API key:
```env
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here
LLM_CATCHER_PROVIDER=openai
```

### Using Ollama

1. Install and start Ollama on your machine
2. Create a `llm_catcher_config.json` file:
```json
{
    "provider": "ollama",
    "llm_model": "qwen2.5-coder",
    "temperature": 0.2
}
```

## Configuration

Settings can be configured through:
1. A `llm_catcher_config.json` file (recommended)
2. Environment variables
3. Direct code configuration

### Using llm_catcher_config.json

Create a `llm_catcher_config.json` file in your project root. You can choose between OpenAI and Ollama configurations:

```json
{
    "provider": "ollama",  // Use "openai" or "ollama"
    "llm_model": "qwen2.5-coder",  // Model name
    "temperature": 0.2
}
```

For OpenAI:
```json
{
    "provider": "openai",
    "llm_model": "gpt-4",
    "temperature": 0.2,
    "openai_api_key": "your-api-key-here"
}
```

### Environment Variables

```env
# Provider Selection
LLM_CATCHER_PROVIDER=openai  # or ollama

# OpenAI Settings
LLM_CATCHER_OPENAI_API_KEY=your-api-key-here  # Required for OpenAI
LLM_CATCHER_LLM_MODEL=gpt-4  # Optional
LLM_CATCHER_TEMPERATURE=0.2  # Optional

# Debug Mode
DEBUG=true  # Enable debug logging
```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `provider` | str | "openai" | LLM provider ("openai" or "ollama") |
| `openai_api_key` | str | None | Your OpenAI API key (required for OpenAI) |
| `llm_model` | str | "gpt-4" | Model name (provider-specific) |
| `temperature` | float | 0.2 | Model temperature (0.0-1.0) |

## Examples

The `examples/` directory contains several examples:

### Basic Usage
```python
from llm_catcher import LLMExceptionDiagnoser

# Initialize diagnoser (will use settings from llm_catcher_config.json)
diagnoser = LLMExceptionDiagnoser()

try:
    result = 1 / 0  # This will raise a ZeroDivisionError
except Exception as e:
    diagnosis = diagnoser.diagnose(e)  # Sync version
    # or
    diagnosis = await diagnoser.async_diagnose(e)  # Async version
    print(diagnosis)
```

### Debug Mode

Set the `DEBUG` environment variable to see detailed diagnostic information:
```bash
DEBUG=true python your_script.py
```

## Notes

- OpenAI API key is required only when using the OpenAI provider
- Ollama must be installed and running for local LLM support
- Settings are validated on initialization
- Stack traces are included in LLM prompts for better diagnosis

## License

MIT License
