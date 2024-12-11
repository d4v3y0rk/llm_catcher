import asyncio
import traceback
from llm_catcher import LLMExceptionDiagnoser
from llm_catcher.settings import get_settings

def standard_error_handler(error: Exception):
    """Standard Python error handling."""
    print(f"\nHandled by standard Python error handling:")
    print(f"Error Type: {type(error).__name__}")
    print(f"Error Message: {str(error)}")

async def demonstrate_unhandled_mode():
    """Demonstrate UNHANDLED mode behavior."""
    print("\n=== Testing UNHANDLED Mode ===")
    print("In this mode, LLM Catcher only handles exceptions that bubble up to the top level")

    # Use settings with UNHANDLED mode
    settings = get_settings()
    settings.handled_exceptions = ["UNHANDLED"]
    diagnoser = LLMExceptionDiagnoser(settings)

    print("\nTest 1: Caught and handled exception")
    try:
        try:
            raise ValueError("This error will be caught and handled normally")
        except ValueError as e:
            # This exception is caught and handled, so LLM won't see it
            standard_error_handler(e)
            # Not re-raising, so it's fully handled here
    except Exception as e:
        # This shouldn't run since the error was handled
        stack_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        diagnosis = await diagnoser.diagnose(stack_trace)
        print(f"LLM Diagnosis: {diagnosis}")

    print("\nTest 2: Uncaught exception bubbling up")
    try:
        # This will raise a NameError with line number info
        def cause_error():
            x = undefined_variable  # This will raise a NameError
            return x
        cause_error()
    except Exception as e:
        # Get full stack trace with line numbers
        stack_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        diagnosis = await diagnoser.diagnose(stack_trace)
        print(f"LLM Diagnosis: {diagnosis}")

async def demonstrate_all_mode():
    """Demonstrate ALL mode behavior."""
    print("\n=== Testing ALL Mode ===")
    print("In this mode, LLM Catcher handles all exceptions, even if they're caught")

    # Use settings with ALL mode
    settings = get_settings()
    settings.handled_exceptions = ["ALL"]
    diagnoser = LLMExceptionDiagnoser(settings)

    print("\nTest 1: Caught and handled exception")
    try:
        try:
            def cause_value_error():
                raise ValueError("This error will be handled by both standard handler and LLM")
            cause_value_error()
        except ValueError as e:
            # Standard handling occurs
            standard_error_handler(e)
            # In ALL mode, we also get LLM diagnosis
            raise  # Re-raise to get LLM diagnosis
    except Exception as e:
        stack_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        diagnosis = await diagnoser.diagnose(stack_trace)
        print(f"LLM Diagnosis: {diagnosis}")

    print("\nTest 2: Uncaught exception bubbling up")
    try:
        def cause_error():
            x = undefined_variable  # This will raise a NameError
            return x
        cause_error()
    except Exception as e:
        stack_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        diagnosis = await diagnoser.diagnose(stack_trace)
        print(f"LLM Diagnosis: {diagnosis}")

async def main():
    print("Running CLI example with LLM Catcher...\n")

    # Initialize diagnoser for settings display
    settings = get_settings()
    diagnoser = LLMExceptionDiagnoser(settings)

    print("Current configuration:")
    print(f"Model: {diagnoser.model}")
    print(f"Temperature: {diagnoser.temperature}")
    print(f"Handled exceptions: {diagnoser.settings.handled_exceptions}")
    print(f"Ignore exceptions: {diagnoser.settings.ignore_exceptions}")
    print(f"Custom handlers: {diagnoser.settings.custom_handlers}")

    # Demonstrate both modes
    await demonstrate_unhandled_mode()
    await demonstrate_all_mode()

if __name__ == "__main__":
    asyncio.run(main())