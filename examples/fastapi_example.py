from fastapi import FastAPI, HTTPException
from llm_catcher import add_exception_diagnoser
from llm_catcher.settings import get_settings
import os
import traceback

app = FastAPI()

# Initialize settings
settings = get_settings()
settings.openai_api_key = os.getenv("OPENAI_API_KEY")  # Optional if set in environment
settings.llm_model = "gpt-4"  # Optional, defaults to gpt-4
settings.handled_exceptions = ["ALL"]  # Handle all exceptions
settings.custom_handlers = {
    "ValueError": "Please explain this error in simple terms"
}

# Add the exception diagnoser middleware
add_exception_diagnoser(app)

@app.get("/")
async def root():
    """Root endpoint that works normally"""
    return {"message": "Hello World"}

@app.get("/error")
async def error():
    """Endpoint that raises a handled exception"""
    # This will be caught and diagnosed
    raise ValueError("This is a test error")

@app.get("/unhandled")
async def unhandled():
    """Endpoint that raises an unhandled exception"""
    # This will be passed through without diagnosis
    raise AttributeError("This error won't be handled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)