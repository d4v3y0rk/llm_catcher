from llm_catcher import LLMExceptionDiagnoser
import asyncio


async def main():
    """Demonstrate basic usage of LLM Catcher."""
    # Initialize diagnoser (will use settings from config.json)
    diagnoser = LLMExceptionDiagnoser()

    try:
        # Cause a simple error
        # Will raise ModuleNotFoundError
        import nonexistent_package  # noqa: F401
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


if __name__ == "__main__":
    print("\nRunning minimal example with LLM Catcher...\n")
    asyncio.run(main())
