import pytest
from llm_catcher import LLMExceptionDiagnoser
from unittest.mock import AsyncMock, MagicMock, patch
import sys


@pytest.fixture
def diagnoser():
    """Fixture to create a diagnoser instance with mocked clients."""
    diagnoser = LLMExceptionDiagnoser(global_handler=False)  # Disable global handler for basic tests
    diagnoser.sync_client = MagicMock()
    diagnoser.async_client = AsyncMock()
    return diagnoser


def test_global_handler():
    """Test that global exception handler is installed correctly."""
    original_excepthook = sys.excepthook
    diagnoser = LLMExceptionDiagnoser(global_handler=True)
    assert sys.excepthook != original_excepthook

    # Test that handler catches and diagnoses
    with patch.object(diagnoser, 'diagnose', return_value="Test diagnosis"):
        with pytest.raises(ZeroDivisionError):
            1/0


def test_decorator_sync():
    """Test the catch decorator with a synchronous function."""
    diagnoser = LLMExceptionDiagnoser(global_handler=False)
    diagnoser.sync_client = MagicMock()
    diagnoser.sync_client.chat.return_value = MagicMock(
        message=MagicMock(content="Test diagnosis")
    )

    @diagnoser.catch
    def failing_function():
        return 1/0

    with pytest.raises(ZeroDivisionError):
        failing_function()


@pytest.mark.asyncio
async def test_decorator_async():
    """Test the catch decorator with an async function."""
    diagnoser = LLMExceptionDiagnoser(global_handler=False)
    diagnoser.async_client = AsyncMock()
    diagnoser.async_client.chat.return_value = MagicMock(
        message=MagicMock(content="Test diagnosis")
    )

    @diagnoser.catch
    async def failing_async_function():
        return 1/0

    with pytest.raises(ZeroDivisionError):
        await failing_async_function()


def test_decorator_preserves_metadata():
    """Test that the decorator preserves function metadata."""
    diagnoser = LLMExceptionDiagnoser(global_handler=False)

    @diagnoser.catch
    def test_function():
        """Test docstring"""
        pass

    assert test_function.__doc__ == "Test docstring"
    assert test_function.__name__ == "test_function"


@pytest.mark.asyncio
async def test_decorator_preserves_async_metadata():
    """Test that the decorator preserves async function metadata."""
    diagnoser = LLMExceptionDiagnoser(global_handler=False)

    @diagnoser.catch
    async def test_async_function():
        """Test async docstring"""
        pass

    assert test_async_function.__doc__ == "Test async docstring"
    assert test_async_function.__name__ == "test_async_function"
