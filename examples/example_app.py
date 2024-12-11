from fastapi import FastAPI, Request, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from llm_catcher.middleware import LLMCatcherMiddleware
from typing import Dict, Any

# Initialize FastAPI app
app = FastAPI(title="LLM Catcher Example")

# Configure custom exception handling
settings = {
    "handled_exceptions": ["ValueError", "TypeError"],
    "ignore_exceptions": ["KeyboardInterrupt"],
    "custom_handlers": {
        "ValueError": "Please analyze this value error specifically."
    }
}

app.add_middleware(
    LLMCatcherMiddleware,
    settings=settings
)

class NameRequest(BaseModel):
    """Request model for name endpoint with validation."""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe"
                }
            ]
        }
    }

class NameResponse(BaseModel):
    """Response model for name endpoint."""
    message: str
    detected_issues: list[str] | None = None

@app.post("/greet", response_model=NameResponse)
async def greet_user(request: NameRequest):
    """
    Endpoint with Pydantic schema validation.
    Greets a user and demonstrates input validation and issue detection.

    Args:
        request (NameRequest): The request containing first and last name

    Returns:
        NameResponse: The greeting message and any detected issues

    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        response = f"Hello, {request.first_name} {request.last_name}! Welcome to our service."
        return NameResponse(
            message=response,
            detected_issues=[]
        )
    except Exception as e:
        logger.error(f"Error processing name request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/echo")
async def echo_data(request: Request):
    """
    Endpoint without Pydantic schema validation.
    Simply echoes back the JSON data it receives.

    Args:
        request (Request): Raw FastAPI request object

    Returns:
        dict: The echoed data or error message
    """
    try:
        data = await request.json()
        return {"message": "Echo successful", "data": data}
    except Exception as e:
        logger.error(f"Error in echo endpoint: {str(e)}")
        # Don't catch the exception, let it propagate to the middleware
        raise

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    try:
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
