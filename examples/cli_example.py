import asyncio
import traceback
from llm_catcher import LLMExceptionDiagnoser
from llm_catcher.settings import get_settings
from loguru import logger

async def demonstrate_unhandled_mode():
    """Demonstrate UNHANDLED mode where only uncaught exceptions are handled."""
    print("\n=== Testing UNHANDLED Mode ===")
    print("In this mode, LLM Catcher only handles exceptions that bubble up to the top level")

    settings = get_settings()
    settings.handled_exceptions = ["UNHANDLED"]
    diagnoser = LLMExceptionDiagnoser(settings=settings)

    print("\nTest 1: Caught and handled exception")
    try:
        raise ValueError("This error will be caught and handled normally")
    except ValueError as e:
        print("\nHandled by standard Python error handling:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")

    print("\nTest 2: Uncaught exception bubbling up")
    try:
        cause_error()
    except Exception as e:
        # Get the full traceback
        stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        # Get diagnosis from LLM
        diagnosis = await diagnoser.diagnose(e, stack_trace)
        print("\nLLM Diagnosis:")
        print(diagnosis)

def cause_error():
    """Function that causes a NameError."""
    x = undefined_variable  # This will raise a NameError

async def demonstrate_all_mode():
    """Demonstrate ALL mode where all exceptions are handled."""
    print("\n=== Testing ALL Mode ===")
    print("In this mode, LLM Catcher handles all exceptions (except ignored ones)")

    settings = get_settings()
    settings.handled_exceptions = ["ALL"]
    diagnoser = LLMExceptionDiagnoser(settings=settings)

    print("\nTest: Exception with custom prompt")
    try:
        x = 1 / 0  # This will raise a ZeroDivisionError
    except Exception as e:
        # Get the full traceback
        stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        # Get diagnosis with custom prompt
        diagnosis = await diagnoser.diagnose(
            e,
            stack_trace,
            custom_prompt="Explain this error in simple terms a beginner would understand:"
        )
        print("\nLLM Diagnosis:")
        print(diagnosis)

async def main():
    """Main function to run the examples."""
    # Print current configuration
    settings = get_settings()
    diagnoser = LLMExceptionDiagnoser(settings=settings)
    print("Current configuration:")
    print(f"Model: {diagnoser.model}")
    print(f"Temperature: {diagnoser.settings.temperature}")
    print(f"Handled exceptions: {diagnoser.settings.handled_exceptions}")
    print(f"Ignore exceptions: {diagnoser.settings.ignore_exceptions}")
    print(f"Custom handlers: {diagnoser.settings.custom_handlers}")

    # Run demonstrations
    await demonstrate_unhandled_mode()
    await demonstrate_all_mode()

if __name__ == "__main__":
    print("\nRunning CLI example with LLM Catcher...\n")
    asyncio.run(main())