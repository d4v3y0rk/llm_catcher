import pytest
from llm_catcher.diagnoser import LLMExceptionDiagnoser
from pydantic import BaseModel, Field
from unittest.mock import patch, MagicMock, AsyncMock

class TestRequest(BaseModel):
    """Test request model for schema validation tests."""
    name: str = Field(..., min_length=2)
    age: int = Field(..., gt=0)

class TestResponse(BaseModel):
    """Test response model for schema validation tests."""
    message: str
    status: bool

@pytest.fixture
def diagnoser(mock_settings):
    """Create a diagnoser instance for testing."""
    return LLMExceptionDiagnoser(api_key="test-key", model="gpt-4")

@pytest.fixture
def sample_stack_trace():
    """Generate a sample stack trace for testing."""
    try:
        raise ValueError("Test error message")
    except ValueError as e:
        import traceback
        return "".join(traceback.format_exception(type(e), e, e.__traceback__))

def test_diagnoser_initialization():
    """Test that diagnoser initializes correctly."""
    diagnoser = LLMExceptionDiagnoser(api_key="test-key")
    assert diagnoser.api_key == "test-key"
    assert diagnoser.model == "gpt-4"  # default model

@pytest.mark.asyncio
async def test_diagnose_basic_error(diagnoser, sample_stack_trace, mock_openai):
    """Test basic error diagnosis without schema information."""
    # Create a new mock for the client
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test diagnosis"))]
    ))
    diagnoser.client = mock_client

    test_exc = ValueError("Test error message")
    result = await diagnoser.diagnose(test_exc, sample_stack_trace)
    assert result == "Test diagnosis"
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_diagnose_with_schema(diagnoser, sample_stack_trace, mock_openai):
    """Test error diagnosis with Pydantic schema information."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test diagnosis with schema"))]
    ))
    diagnoser.client = mock_client

    test_exc = ValueError("Test error message")
    result = await diagnoser.diagnose(
        test_exc,
        sample_stack_trace,
        request_model=TestRequest,
        response_model=TestResponse,
        request_data={"name": "a", "age": 0}  # invalid data
    )
    assert result == "Test diagnosis with schema"
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_diagnose_openai_error(diagnoser, sample_stack_trace, mock_openai):
    """Test handling of OpenAI API errors."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    diagnoser.client = mock_client

    test_exc = ValueError("Test error message")
    result = await diagnoser.diagnose(test_exc, sample_stack_trace)
    assert "Failed to contact LLM for diagnosis" in result
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_diagnose_with_invalid_schema(diagnoser, sample_stack_trace, mock_openai):
    """Test diagnosis with invalid schema data."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Schema validation error diagnosis"))]
    ))
    diagnoser.client = mock_client

    test_exc = ValueError("Test error message")
    result = await diagnoser.diagnose(
        test_exc,
        sample_stack_trace,
        request_model=TestRequest,
        request_data={"invalid": "data"}  # completely invalid data
    )
    assert result == "Schema validation error diagnosis"
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_diagnose_with_custom_prompt(diagnoser, sample_stack_trace, mock_openai):
    """Test diagnosis with custom prompt."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Custom diagnosis"))]
    ))
    diagnoser.client = mock_client

    test_exc = ValueError("Test error message")
    result = await diagnoser.diagnose(
        test_exc,
        sample_stack_trace,
        custom_prompt="Custom analysis instructions"
    )
    assert result == "Custom diagnosis"
    mock_client.chat.completions.create.assert_called_once()
