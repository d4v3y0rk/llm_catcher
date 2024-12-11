import pytest
from pydantic_settings import BaseSettings
from llm_catcher.settings import Settings
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests."""
    with patch('llm_catcher.settings.Settings') as mock_settings:
        mock_settings.return_value = Settings(
            openai_api_key="test-key",
            llm_model="gpt-4",
            temperature=0.2,
            handled_exceptions=["ValueError", "TypeError"],
            ignore_exceptions=["KeyboardInterrupt"],
            custom_handlers={"ValueError": "Custom prompt for ValueError"}
        )
        yield mock_settings

@pytest.fixture(autouse=True)
def mock_openai():
    """Mock OpenAI API calls."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test diagnosis"))]

        # Create an async mock for create method
        async def async_create(*args, **kwargs):
            return mock_response

        mock_completions.create = AsyncMock(side_effect=async_create)
        mock_chat.completions = mock_completions
        mock_client.chat = mock_chat
        mock_openai.return_value = mock_client

        yield mock_client

@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    app = FastAPI()

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    @app.get("/ignored_error")
    async def ignored_error_endpoint():
        raise KeyboardInterrupt()

    @app.get("/unhandled_error")
    async def unhandled_error_endpoint():
        raise AttributeError("Unhandled error")

    return app

@pytest.fixture
def test_client(test_app):
    """Create a test client."""
    return TestClient(test_app)