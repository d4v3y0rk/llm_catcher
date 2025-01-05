from fastapi import FastAPI
from llm_catcher import LLMExceptionDiagnoser

app = FastAPI()
diagnoser = LLMExceptionDiagnoser()

@app.get("/")
async def root():
    """Root endpoint that works normally"""
    return {"message": "Hello World"}

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