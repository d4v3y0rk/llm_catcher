import pytest
from llm_catcher import LLMExceptionDiagnoser
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def diagnoser():
    """Fixture to create a diagnoser instance with mocked clients."""
    diagnoser = LLMExceptionDiagnoser()
    diagnoser.sync_client = MagicMock()
    diagnoser.async_client = AsyncMock()
    return diagnoser

def test_sync_diagnose_formatted(diagnoser):
    """Test the sync diagnose method with formatted output."""
    error = ZeroDivisionError("division by zero")
    diagnoser.sync_client.chat.return_value = MagicMock(
        message=MagicMock(content="Diagnosis for ZeroDivisionError")
    )

    diagnosis = diagnoser.diagnose(error)
    assert "LLM DIAGNOSIS" in diagnosis
    assert "Diagnosis for ZeroDivisionError" in diagnosis

def test_sync_diagnose_plain(diagnoser):
    """Test the sync diagnose method with plain text output."""
    error = ZeroDivisionError("division by zero")
    diagnoser.sync_client.chat.return_value = MagicMock(
        message=MagicMock(content="Diagnosis for ZeroDivisionError")
    )

    diagnosis = diagnoser.diagnose(error, formatted=False)
    assert diagnosis == "Diagnosis for ZeroDivisionError"

@pytest.mark.asyncio
async def test_async_diagnose_formatted(diagnoser):
    """Test the async diagnose method with formatted output."""
    error = ZeroDivisionError("division by zero")
    diagnoser.async_client.chat.return_value = MagicMock(
        message=MagicMock(content="Diagnosis for ZeroDivisionError")
    )

    diagnosis = await diagnoser.async_diagnose(error)
    assert "LLM DIAGNOSIS" in diagnosis
    assert "Diagnosis for ZeroDivisionError" in diagnosis

@pytest.mark.asyncio
async def test_async_diagnose_plain(diagnoser):
    """Test the async diagnose method with plain text output."""
    error = ZeroDivisionError("division by zero")
    diagnoser.async_client.chat.return_value = MagicMock(
        message=MagicMock(content="Diagnosis for ZeroDivisionError")
    )

    diagnosis = await diagnoser.async_diagnose(error, formatted=False)
    assert diagnosis == "Diagnosis for ZeroDivisionError"