import asyncio
import traceback
from llm_catcher.diagnoser import LLMExceptionDiagnoser
from typing import List, Dict
import json
from loguru import logger

class CustomError(Exception):
    """Custom error that has its own handler."""
    pass

class DataProcessor:
    def process_numbers(self, numbers: List[int]) -> Dict[str, float]:
        """Process a list of numbers with some risky operations."""
        total = sum(numbers)
        average = total / len(numbers)  # Potential ZeroDivisionError
        result = {
            "total": total,
            "average": average,
            "first_item_squared": numbers[0] ** 2,  # Potential IndexError
        }
        return result

    def load_data(self, filename: str) -> Dict:
        """Load and parse JSON data from a file."""
        with open(filename, 'r') as f:  # Potential FileNotFoundError
            data = json.load(f)  # Potential JSONDecodeError
        return data

    def custom_operation(self):
        """Operation that raises our custom error."""
        raise CustomError("This is a custom error")

async def handle_error(diagnoser: LLMExceptionDiagnoser, e: Exception):
    """Handle an error with the diagnoser."""
    stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    diagnosis = await diagnoser.diagnose(stack_trace)
    print("\nError occurred! 🚨")
    print(f"Exception type: {type(e).__name__}")
    print(f"\nDiagnosis:\n{diagnosis}")

def custom_error_handler(e: CustomError):
    """Custom handler for CustomError."""
    print("\nCustom handler caught an error! 🎯")
    print(f"Message: {str(e)}")
    return True

async def run_examples():
    """Run the example error cases."""
    # Initialize the diagnoser
    diagnoser = LLMExceptionDiagnoser()
    processor = DataProcessor()

    # Register custom handler
    custom_handlers = {
        CustomError: custom_error_handler
    }

    print("\n1. Testing ZeroDivisionError (unhandled):")
    try:
        numbers = []  # Empty list to trigger error
        result = processor.process_numbers(numbers)
        print(f"Processed result: {result}")
    except Exception as e:
        # This will be caught by LLM Catcher in both UNHANDLED and ALL modes
        await handle_error(diagnoser, e)

    print("\n2. Testing CustomError (has custom handler):")
    try:
        processor.custom_operation()
    except CustomError as e:
        if custom_handlers.get(type(e)):
            # This will be handled by custom handler in UNHANDLED mode
            # but will be caught by LLM Catcher in ALL mode
            handled = custom_handlers[type(e)](e)
            if not handled and 'ALL' in diagnoser.settings.handled_exceptions:
                await handle_error(diagnoser, e)
        else:
            await handle_error(diagnoser, e)

    print("\n3. Testing FileNotFoundError:")
    try:
        data = processor.load_data("nonexistent.json")
        print(f"Loaded data: {data}")
    except Exception as e:
        # This will be caught by LLM Catcher in both modes
        await handle_error(diagnoser, e)

async def main():
    print("Running CLI example with LLM Catcher...\n")

    # Initialize diagnoser for settings display
    diagnoser = LLMExceptionDiagnoser()

    print("Current configuration:")
    print(f"Model: {diagnoser.model}")
    print(f"Temperature: {diagnoser.temperature}")
    print(f"Handled exceptions: {diagnoser.settings.handled_exceptions}")
    print(f"Ignore exceptions: {diagnoser.settings.ignore_exceptions}")
    print(f"Custom handlers: {diagnoser.settings.custom_handlers}")

    print("\nTry changing LLM_CATCHER_HANDLED_EXCEPTIONS in .env to:")
    print("- UNHANDLED (default): Only handles exceptions without custom handlers")
    print("- ALL: Handles all exceptions, even those with custom handlers")

    await run_examples()

if __name__ == "__main__":
    asyncio.run(main())