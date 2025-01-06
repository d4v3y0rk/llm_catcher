from llm_catcher import LLMExceptionDiagnoser
import asyncio


async def main():
    """Demonstrate basic usage of LLM Catcher."""
    # Initialize diagnoser (global handler is enabled by default)
    diagnoser = LLMExceptionDiagnoser()

    # Or explicitly disable the global handler
    # diagnoser = LLMExceptionDiagnoser(global_handler=False)

    try:
        # Cause a simple error
        # Will raise ModuleNotFoundError
        potato  # noqa: F821
    except Exception as e:
        # Get diagnosis from LLM
        diagnosis = await diagnoser.async_diagnose(e)
        print(diagnosis)

    try:
        # Will raise ZeroDivisionError
        _ = 1 / 0
    except Exception as e:
        # Get diagnosis from LLM
        diagnosis = diagnoser.diagnose(e)
        print(diagnosis)

    # This unhandled exception will be caught by the global handler
    import pandas  # noqa: F401, F841


if __name__ == "__main__":
    print("\nRunning minimal example with LLM Catcher...\n")
    asyncio.run(main())
