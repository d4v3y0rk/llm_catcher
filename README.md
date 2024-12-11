# LLM Catcher

LLM Catcher is a Python library that uses Large Language Models to diagnose and provide helpful explanations for exceptions in both FastAPI applications and CLI scripts.

## Installation

```bash
pip install llm-catcher
```

## Configuration

LLM Catcher requires only an OpenAI API key to get started. All other settings have sensible defaults.

### Minimal Configuration
```env
# Only required setting
LLM_CATCHER_OPENAI_API_KEY=your-openai-api-key
```

With this minimal configuration, LLM Catcher will:
- Only diagnose unhandled exceptions (won't interfere with your existing error handlers)
- Ignore KeyboardInterrupt and SystemExit
- Use GPT-4 with temperature 0.2

### Exception Handling Configuration

There are three ways to configure which exceptions are handled:

1. Handle only unhandled exceptions (default):
```env
# Simple format (recommended)
LLM_CATCHER_HANDLED_EXCEPTIONS=UNHANDLED

# Or JSON array format
LLM_CATCHER_HANDLED_EXCEPTIONS=["UNHANDLED"]
```

2. Handle all exceptions:
```env
# Simple format (recommended)
LLM_CATCHER_HANDLED_EXCEPTIONS=ALL

# Or JSON array format
LLM_CATCHER_HANDLED_EXCEPTIONS=["ALL"]
```

3. Handle specific exceptions:
```env
# Simple format (comma-separated)
LLM_CATCHER_HANDLED_EXCEPTIONS=ValueError,TypeError,ValidationError

# Or JSON array format
LLM_CATCHER_HANDLED_EXCEPTIONS=["ValueError", "TypeError", "ValidationError"]
```

### Ignoring Exceptions

Specify exceptions to ignore (these take precedence over handled exceptions):
```env
# Simple format (recommended)
LLM_CATCHER_IGNORE_EXCEPTIONS=KeyboardInterrupt,SystemExit

# Or JSON array format
LLM_CATCHER_IGNORE_EXCEPTIONS=["KeyboardInterrupt", "SystemExit"]
```

### Custom Prompts

Add custom prompts for specific exception types:
```env
# JSON format required for custom handlers
LLM_CATCHER_CUSTOM_HANDLERS={
    "ValueError": """
        Please analyze this value error and provide:
        1. The exact file and line where it occurred
        2. What caused the invalid value
        3. Specific code suggestions to fix it
    """,
    "ZeroDivisionError": """
        Explain the division error that occurred:
        1. Identify the file and line number
        2. Show why the division by zero happened
        3. Provide a code example showing how to prevent it
    """
}
```

### Model Settings
```env
# Optional model settings with their defaults
LLM_CATCHER_LLM_MODEL=gpt-4
LLM_CATCHER_TEMPERATURE=0.2
```

## Usage Examples

### FastAPI with UNHANDLED (Default)

Only handle exceptions that aren't caught by other handlers:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from llm_catcher.middleware import LLMCatcherMiddleware

app = FastAPI()

# Add middleware with default settings (UNHANDLED)
app.add_middleware(LLMCatcherMiddleware)

# Your custom handler will be respected
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": "Custom handler: Invalid value provided"}
    )

@app.get("/example")
async def example_endpoint():
    value = int("not a number")  # This will use your custom handler
    return {"value": value}

# Example response for unhandled exception:
{
    "error": "Internal Server Error",
    "diagnosis": "Error occurred in '/app/endpoints.py', line 45: The string 'not a number' cannot be converted to an integer. The int() function expects a string containing valid numeric characters. Consider adding input validation or using a try/catch block to handle invalid input.",
    "exception_type": "ValueError",
    "has_schema_info": false
}
```

### FastAPI with ALL

Handle all exceptions except those explicitly ignored:

```python
from fastapi import FastAPI
from llm_catcher.middleware import LLMCatcherMiddleware

app = FastAPI()

settings = {
    "handled_exceptions": ["ALL"],
    "ignore_exceptions": ["KeyboardInterrupt", "SystemExit"]
}
app.add_middleware(LLMCatcherMiddleware, settings=settings)

@app.get("/example")
async def example_endpoint():
    value = int("not a number")  # This will be caught and diagnosed
    return {"value": value}
```

### FastAPI with Specific Exceptions

Handle only certain types of exceptions:

```python
from fastapi import FastAPI
from llm_catcher.middleware import LLMCatcherMiddleware

app = FastAPI()

settings = {
    "handled_exceptions": ["ValueError", "TypeError", "ValidationError"],
    "custom_handlers": {
        "ValueError": "Please analyze this value error with file and line information"
    }
}
app.add_middleware(LLMCatcherMiddleware, settings=settings)
```

## Usage in CLI Applications

For CLI applications, use the diagnoser directly with async/await:

```python
import asyncio
import traceback
from llm_catcher.diagnoser import LLMExceptionDiagnoser

async def handle_error(diagnoser: LLMExceptionDiagnoser, e: Exception):
    """Handle an error with the diagnoser."""
    stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    diagnosis = await diagnoser.diagnose(stack_trace)
    print(f"\nError occurred! 🚨")
    print(f"Exception type: {type(e).__name__}")
    print(f"\nDiagnosis:\n{diagnosis}")

async def main():
    # Initialize the diagnoser
    diagnoser = LLMExceptionDiagnoser()

    try:
        # Your code that might raise exceptions
        result = perform_risky_operation()
        print(result)
    except Exception as e:
        await handle_error(diagnoser, e)

def perform_risky_operation():
    # This will raise an exception
    return 1 / 0

if __name__ == "__main__":
    asyncio.run(main())

# Example output:
# Error occurred! 🚨
# Exception type: ZeroDivisionError
#
# Diagnosis:
# Error in 'examples/cli_example.py', line 42: A division by zero error occurred in the
# perform_risky_operation function. The code attempted to divide 1 by 0, which is
# mathematically undefined. Add a check before the division operation:
# if denominator != 0: result = numerator / denominator
```

## Special Configuration Options

### ALL Handler
The `ALL` option will catch and diagnose all exceptions except those in `ignore_exceptions`:

```python
settings = {
    "handled_exceptions": ["ALL"],
    "ignore_exceptions": ["KeyboardInterrupt", "SystemExit"]
}
app.add_middleware(LLMCatcherMiddleware, settings=settings)
```

### UNHANDLED Handler
The `UNHANDLED` option will only catch exceptions that aren't handled by other error handlers:

```python
settings = {
    "handled_exceptions": ["UNHANDLED"],
    "ignore_exceptions": ["KeyboardInterrupt"]
}
app.add_middleware(LLMCatcherMiddleware, settings=settings)
```

### Handling Priority

When using these special options, the handling priority is:

1. `ignore_exceptions` (always checked first)
2. Existing FastAPI exception handlers (when using UNHANDLED)
3. LLM Catcher handlers based on configuration:
   - `ALL`: Handles all exceptions not ignored
   - `UNHANDLED`: Only handles exceptions not caught by other handlers
   - Specific exceptions: Only handles listed exceptions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.