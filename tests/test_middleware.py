import pytest
from fastapi import FastAPI
from llm_catcher import add_exception_diagnoser
from llm_catcher.settings import get_settings
from fastapi.testclient import TestClient

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    settings = get_settings()
    settings.handled_exceptions = ["ValueError"]
    settings.ignore_exceptions = ["AttributeError"]
    add_exception_diagnoser(app)
    return app

def test_middleware_handles_configured_exception(app):
    """Test middleware handles configured exceptions."""
    client = TestClient(app)

    @app.get("/error")
    async def error():
        raise ValueError("Test error")

    response = client.get("/error")
    assert response.status_code == 500
    assert "diagnosis" in response.json()

def test_middleware_ignores_configured_exception(app):
    """Test middleware ignores configured exceptions."""
    client = TestClient(app)

    @app.get("/ignored")
    async def ignored():
        raise AttributeError("Ignored error")

    with pytest.raises(AttributeError):
        client.get("/ignored")

def test_middleware_passes_unhandled_exception(app):
    """Test middleware passes through unhandled exceptions."""
    client = TestClient(app)

    @app.get("/unhandled")
    async def unhandled():
        raise TypeError("Unhandled error")

    with pytest.raises(TypeError):
        client.get("/unhandled")
