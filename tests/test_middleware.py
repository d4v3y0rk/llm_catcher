import pytest
from fastapi import FastAPI
from llm_catcher.middleware import LLMCatcherMiddleware
from llm_catcher.diagnoser import LLMExceptionDiagnoser
from fastapi.testclient import TestClient
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_middleware_handles_configured_exception(test_client, test_app, mock_openai):
    """Test that middleware handles configured exceptions."""
    settings = {
        "handled_exceptions": ["ValueError"],
        "custom_handlers": {
            "ValueError": "Custom prompt"
        }
    }

    # Create a mock diagnoser
    mock_diagnoser = MagicMock(spec=LLMExceptionDiagnoser)
    mock_diagnoser.diagnose = AsyncMock(return_value="Handled ValueError")

    # Patch the diagnoser class and its instantiation
    with patch('llm_catcher.middleware.LLMExceptionDiagnoser') as mock_diagnoser_class:
        mock_diagnoser_class.return_value = mock_diagnoser

        test_app.add_middleware(LLMCatcherMiddleware, settings=settings)
        client = TestClient(test_app)

        response = client.get("/error")
        assert response.status_code == 500
        assert response.json()["diagnosis"] == "Handled ValueError"
        mock_diagnoser.diagnose.assert_called_once()

def test_middleware_ignores_configured_exception(test_client, test_app):
    """Test that middleware ignores configured exceptions."""
    settings = {
        "handled_exceptions": ["ValueError"],
        "ignore_exceptions": ["KeyboardInterrupt"]
    }

    test_app.add_middleware(LLMCatcherMiddleware, settings=settings)
    client = TestClient(test_app)

    with pytest.raises(KeyboardInterrupt):
        client.get("/ignored_error")

def test_middleware_passes_unhandled_exception(test_client, test_app):
    """Test that middleware passes through unhandled exceptions."""
    settings = {
        "handled_exceptions": ["ValueError"]
    }

    test_app.add_middleware(LLMCatcherMiddleware, settings=settings)
    client = TestClient(test_app)

    with pytest.raises(AttributeError):
        client.get("/unhandled_error")
