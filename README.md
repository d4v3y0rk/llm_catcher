# LLM Catcher

Stack traces: the unsung villains of debugging.
Why wrestle with a wall of cryptic error messages when you could let LLM Catcher do the heavy lifting?

LLM Catcher is your debugging sidekick—a Python library that teams up with Large Language Models (Ollama or OpenAI) to decode those pesky exceptions. Instead of copy-pasting a stack trace into your LLM chat and then shuffling back to your IDE, LLM Catcher delivers instant, insightful fixes right in your logs.

Stop debugging the old-fashioned way. Catch the errors, not the headaches!

## Features

- Exception diagnosis using LLMs (Ollama or OpenAI)
- Support for local LLMs through Ollama
- OpenAI integration for cloud-based models
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

### Basic Usage

```python
from llm_catcher import LLMExceptionDiagnoser

# Initialize diagnoser (uses Ollama with qwen2.5-coder by default)
diagnoser = LLMExceptionDiagnoser()

try:
    result = 1 / 0  # This will raise a ZeroDivisionError
except Exception as e:
    # Use the diagnose method with formatted=False for plain text output
    diagnosis = diagnoser.diagnose(e, formatted=False)
    print(diagnosis)
```

### Using with FastAPI

Here's an example of using LLM Catcher with FastAPI, utilizing the `formatted` option for plain text output:

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
        # Use the async_diagnose method with formatted=False for plain text output
        diagnosis = await diagnoser.async_diagnose(e, formatted=False)
        return {"error": str(e), "diagnosis": diagnosis}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
```

### Formatting Option

The `diagnose` and `async_diagnose` methods have an optional `formatted` parameter:

- `formatted=True` (default): Returns the diagnosis with clear formatting and boundaries.
- `formatted=False`: Returns the diagnosis as plain text, suitable for JSON responses or other contexts where formatting might be undesirable.

This flexibility allows you to tailor the output to your specific needs, whether for console logs or API responses.

### Default Setup

Out of the box, LLM Catcher uses these defaults:
- Provider: `ollama`
- Model: `qwen2.5-coder`

For OpenAI configurations:
- Temperature: `0.2` (only used with OpenAI)

This means you can start using LLM Catcher immediately after installing Ollama and pulling the model.

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

- Ollama must be installed and running for local LLM support (default)
- OpenAI API key is required only when using OpenAI provider
- Settings are validated on initialization
- Stack traces are included in LLM prompts for better diagnosis

## Design Decisions

### Why No Decorators?

While decorators might seem convenient for error handling, we deliberately chose not to provide them because:

1. Explicit error handling with try/except blocks is more Pythonic
2. Decorators can mask the actual flow of error handling
3. Try/except blocks give developers more control over:
   - Which errors to catch
   - How to handle different types of errors
   - When to suppress vs propagate errors
   - Where to place the diagnosis in their logging flow

### Caveats

#### Stack Trace Output

LLM Catcher cannot prevent all stack traces from appearing in your output. This is because:

1. Python modules can write directly to stderr/stdout
2. Some modules print stack traces during their import or initialization
3. Third-party libraries may have their own error handling that prints traces
4. System-level errors may bypass Python's exception handling

For example, when importing a module with missing dependencies, you might see output like:
```
ImportError: cannot import name 'foo' from 'some_module'
[stack trace from the module...]
```

This is normal and expected - LLM Catcher will still provide its diagnosis, but it cannot prevent other modules from writing their own error output.

## License

MIT License
