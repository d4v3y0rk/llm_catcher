from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from llm_catcher.middleware import LLMCatcherMiddleware
from llm_catcher.settings import Settings
from typing import List, Dict, Optional
import json
import traceback

app = FastAPI(title="LLM Catcher Demo")

# Configure exception handling with Settings object
settings = Settings(
    handled_exceptions=["UNHANDLED"],  # Only handle uncaught exceptions
    ignore_exceptions=["KeyboardInterrupt"],
    custom_handlers={
        "ValueError": "This is a validation error in the API. Please check: \n1. Input data types\n2. Required fields\n3. Value ranges",
        "ZeroDivisionError": "This is a division by zero error. Check for zero values in division operations."
    }
)

# Add the middleware with settings
app.add_middleware(LLMCatcherMiddleware, settings=settings)

# Custom handler that LLM Catcher will respect when using UNHANDLED
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Custom handler for ValueError that returns a 400 response."""
    return JSONResponse(
        status_code=400,
        content={"message": "Custom handler: Invalid value provided"}
    )

class NumbersRequest(BaseModel):
    """Request model for number processing."""
    numbers: List[float] = Field(...,
        description="List of numbers to process",
        example=[1.0, 2.0, 3.0]
    )
    operation: str = Field(...,
        description="Operation to perform",
        example="sum",
        pattern="^(sum|average|multiply)$"
    )

class ProcessingResponse(BaseModel):
    """Response model for processed data."""
    result: float = Field(..., description="Result of the operation")
    operation: str = Field(..., description="Operation that was performed")
    input_count: int = Field(..., description="Number of input values processed")

@app.post("/process",
    response_model=ProcessingResponse,
    description="Process a list of numbers with the specified operation"
)
async def process_numbers(request: NumbersRequest):
    """
    Process a list of numbers based on the specified operation.
    Demonstrates various potential errors that will be caught and diagnosed by LLM Catcher.

    Possible errors:
    - ValueError: Empty number list or invalid operation
    - ZeroDivisionError: Division by zero in average calculation
    - TypeError: Invalid number types
    """
    try:
        if not request.numbers:
            raise ValueError("Empty number list provided")

        result = 0
        if request.operation == "sum":
            result = sum(request.numbers)
        elif request.operation == "average":
            if len(request.numbers) == 0:
                raise ZeroDivisionError("Cannot calculate average of empty list")
            result = sum(request.numbers) / len(request.numbers)
        elif request.operation == "multiply":
            result = 1
            for num in request.numbers:
                result *= num
        else:
            raise ValueError(f"Unknown operation: {request.operation}")

        return ProcessingResponse(
            result=result,
            operation=request.operation,
            input_count=len(request.numbers)
        )
    except Exception as e:
        # Let LLM Catcher handle it through middleware
        raise

class DataRequest(BaseModel):
    """Request model for data loading."""
    filename: str = Field(...,
        description="Name of the JSON file to load",
        pattern="^[a-zA-Z0-9_-]+$"
    )

@app.get("/data/{filename}",
    description="Load and return data from a JSON file"
)
async def get_data(filename: str):
    """
    Load data from a JSON file.
    Demonstrates file handling errors that will be caught and diagnosed by LLM Catcher.

    Possible errors:
    - FileNotFoundError: File doesn't exist
    - JSONDecodeError: Invalid JSON format
    - PermissionError: No read access
    """
    try:
        with open(f"data/{filename}.json", 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename}.json not found")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file {filename}.json")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"No permission to read {filename}.json")

@app.get("/error-examples/{error_type}",
    description="Endpoint to trigger various types of errors for testing"
)
async def trigger_error(error_type: str):
    """
    Endpoint to deliberately trigger different types of errors
    to demonstrate LLM Catcher's diagnosis capabilities.
    """
    if error_type == "value":
        return int("not a number")  # ValueError
    elif error_type == "zero":
        return 1 / 0  # ZeroDivisionError
    elif error_type == "index":
        return [1, 2, 3][999]  # IndexError
    elif error_type == "type":
        return "string" + 42  # TypeError
    elif error_type == "key":
        empty_dict = {}
        return empty_dict["nonexistent"]  # KeyError
    elif error_type == "attribute":
        class Empty: pass
        return Empty().nonexistent  # AttributeError
    else:
        return {"message": "No error triggered"}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI example with LLM Catcher...")
    print("\nConfiguration:")
    print(f"Handled exceptions: {settings.handled_exceptions}")
    print(f"Ignore exceptions: {settings.ignore_exceptions}")
    print(f"Custom handlers: {settings.custom_handlers}")
    print(f"Handle unhandled only: {settings.handle_unhandled_only}")
    uvicorn.run(app, host="0.0.0.0", port=8000)