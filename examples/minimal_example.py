from llm_catcher import LLMExceptionDiagnoser
from llm_catcher.settings import get_settings
import asyncio
import traceback

async def main():
    """Demonstrate basic usage of LLM Catcher."""
    # Initialize settings and diagnoser
    settings = get_settings()
    diagnoser = LLMExceptionDiagnoser(settings=settings)

    try:
        # Cause a simple error
        result = 1 / 0  # This will raise a ZeroDivisionError
    except Exception as e:
        # Get the full traceback
        stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))

        # Get diagnosis from LLM
        diagnosis = await diagnoser.diagnose(
            exc=e,
            stack_trace=stack_trace
        )

        print("\nError occurred!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nLLM Diagnosis:")
        print(diagnosis)

if __name__ == "__main__":
    print("\nRunning minimal example with LLM Catcher...\n")
    asyncio.run(main())