from llm_catcher import LLMExceptionDiagnoser
import asyncio

async def main():
    """Demonstrate basic usage of LLM Catcher."""
    # Initialize settings and diagnoser
    diagnoser = LLMExceptionDiagnoser()

    try:
        # Cause a simple error
        result = 1 / 0  # This will raise a ZeroDivisionError
    except Exception as e:
        # Get diagnosis from LLM
        diagnosis = await diagnoser.async_diagnose(e)
        print(diagnosis)

    try:
        result = 1 / 0  # This will raise a ZeroDivisionError
    except Exception as e:
        # Get diagnosis from LLM
        diagnosis = diagnoser.diagnose(e)
        print(diagnosis)

if __name__ == "__main__":
    print("\nRunning minimal example with LLM Catcher...\n")
    asyncio.run(main())