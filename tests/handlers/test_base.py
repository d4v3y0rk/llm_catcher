import pytest
from llm_catcher.handlers.base import BaseExceptionHandler
from llm_catcher.diagnoser import LLMExceptionDiagnoser
from unittest.mock import MagicMock

class TestHandler(BaseExceptionHandler):
    """Test implementation of BaseExceptionHandler."""
    async def handle_exception(self, exc: Exception, **kwargs):
        return f"Handled {exc.__class__.__name__}"

@pytest.fixture
def handler():
    """Create a test handler instance."""
    mock_diagnoser = MagicMock(spec=LLMExceptionDiagnoser)
    settings = {
        "handled_exceptions": ["ValueError", "TypeError"],
        "ignore_exceptions": ["KeyboardInterrupt"],
        "custom_handlers": {
            "ValueError": "Custom prompt for ValueError"
        }
    }
    return TestHandler(mock_diagnoser, settings)

def test_handler_initialization(handler):
    """Test handler initialization with settings."""
    assert len(handler.handled_exceptions) == 2
    assert len(handler.ignore_exceptions) == 1

def test_should_handle_exceptions(handler):
    """Test exception handling decisions."""
    assert handler.should_handle(ValueError())
    assert handler.should_handle(TypeError())
    assert not handler.should_handle(KeyboardInterrupt())
    assert not handler.should_handle(AttributeError())

def test_custom_prompt_retrieval(handler):
    """Test custom prompt retrieval for exceptions."""
    value_error = ValueError()
    type_error = TypeError()

    assert handler.get_custom_prompt(value_error) == "Custom prompt for ValueError"
    assert handler.get_custom_prompt(type_error) is None