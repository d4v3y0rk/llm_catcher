import pytest
from llm_catcher.handlers.fastapi_handler import FastAPIExceptionHandler
from llm_catcher.diagnoser import LLMExceptionDiagnoser
from unittest.mock import MagicMock, patch
from fastapi import Request
from fastapi.responses import JSONResponse
from unittest.mock import AsyncMock

@pytest.fixture
def handler():
    """Create a FastAPI handler instance."""
    mock_diagnoser = MagicMock(spec=LLMExceptionDiagnoser)
    mock_diagnoser.diagnose.return_value = "Test diagnosis"
    settings = {
        "handled_exceptions": ["ValueError"],
        "custom_handlers": {
            "ValueError": "Custom prompt"
        }
    }
    return FastAPIExceptionHandler(mock_diagnoser, settings)

@pytest.mark.asyncio
async def test_handle_exception_with_request(handler):
    """Test exception handling with a valid request."""
    mock_request = MagicMock(spec=Request)
    mock_request.scope = {"route": None}

    response = await handler.handle_exception(
        ValueError("Test error"),
        request=mock_request
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert "diagnosis" in response.body.decode()

@pytest.mark.asyncio
async def test_handle_exception_without_request(handler):
    """Test exception handling without a request object."""
    response = await handler.handle_exception(ValueError("Test error"))

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = response.body.decode()
    assert "error" in response_data
    assert "diagnosis" in response_data

@pytest.mark.asyncio
async def test_handle_exception_with_custom_prompt(handler, mock_openai):
    """Test exception handling with custom prompt."""
    # Create test data
    test_data = {"test": "data"}
    test_error = ValueError("Test error")

    # Create a more complete mock request
    mock_request = MagicMock()
    mock_request.__class__ = Request  # Make isinstance(request, Request) return True
    mock_request.scope = {
        "route": MagicMock(
            endpoint=MagicMock(
                __annotations__={
                    "request": Request,
                    "return": dict
                }
            )
        )
    }

    # Mock the request.json() method
    mock_request.json = AsyncMock(return_value=test_data)

    # Create a proper mock diagnoser with async context
    mock_diagnoser = MagicMock(spec=LLMExceptionDiagnoser)
    mock_diagnoser.diagnose = AsyncMock(return_value="Custom diagnosis")

    # Create a new handler with our mock diagnoser
    settings = {
        "handled_exceptions": ["ValueError"],
        "custom_handlers": {
            "ValueError": "Custom prompt"
        }
    }
    handler = FastAPIExceptionHandler(mock_diagnoser, settings)

    # Handle the exception
    response = await handler.handle_exception(
        test_error,
        request=mock_request
    )

    # Verify response
    assert isinstance(response, JSONResponse)
    response_data = response.body.decode('utf-8')  # Get raw JSON string
    assert '"diagnosis":"Custom diagnosis"' in response_data
    mock_diagnoser.diagnose.assert_called_once()

    # Verify the diagnosis was called with the correct arguments
    call_args, call_kwargs = mock_diagnoser.diagnose.call_args
    assert call_kwargs.get('request_data') == test_data
    assert call_kwargs.get('custom_prompt') is not None