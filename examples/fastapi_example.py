from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from llm_catcher.middleware import LLMCatcherMiddleware
from typing import List, Dict, Optional
import json

app = FastAPI(title="LLM Catcher Demo")

# Configure exception handling
settings = {
    "handled_exceptions": ["UNHANDLED"],
    "ignore_exceptions": ["KeyboardInterrupt"]
}

# Add the middleware
app.add_middleware(LLMCatcherMiddleware, settings=settings)

# Custom handler that LLM Catcher will respect when using UNHANDLED
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": "Custom handler: Invalid value provided"}
    )

class NumbersRequest(BaseModel):
    """Request model for number processing."""
    numbers: List[float] = Field(..., description="List of numbers to process")
    operation: str = Field(..., description="Operation to perform (sum, average, multiply)")

class ProcessingResponse(BaseModel):
    """Response model for processed data."""
    result: float
    operation: str
    input_count: int

@app.post("/process", response_model=ProcessingResponse)
async def process_numbers(request: NumbersRequest):
    """
    Process a list of numbers based on the specified operation.
    Demonstrates various potential errors that will be caught and diagnosed.
    """
    if not request.numbers:
        raise ValueError("Empty number list provided")

    result = 0
    if request.operation == "sum":
        result = sum(request.numbers)
    elif request.operation == "average":
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

@app.get("/data/{filename}")
async def get_data(filename: str):
    """
    Load data from a JSON file.
    Demonstrates file handling errors that will be caught and diagnosed.
    """
    try:
        with open(f"data/{filename}.json", 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {filename}.json not found")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file {filename}.json")

@app.get("/error-examples/{error_type}")
async def trigger_error(error_type: str):
    """
    Endpoint to deliberately trigger different types of errors
    to demonstrate LLM Catcher's diagnosis capabilities.
    """
    if error_type == "value":
        return int("not a number")
    elif error_type == "zero":
        return 1 / 0
    elif error_type == "index":
        return [1, 2, 3][999]
    elif error_type == "type":
        return "string" + 42
    else:
        return {"message": "No error triggered"}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI example with LLM Catcher...")
    uvicorn.run(app, host="0.0.0.0", port=8000)