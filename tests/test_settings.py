import pytest
from llm_catcher.settings import Settings
from typing import List, Dict
import json
import os

@pytest.fixture(autouse=True)
def clear_env():
    """Clear environment variables before each test."""
    env_vars = [key for key in os.environ if key.startswith('LLM_CATCHER_')]
    for key in env_vars:
        del os.environ[key]
    yield

@pytest.mark.parametrize("env_value,expected", [
    # Test UNHANDLED format variations
    ("UNHANDLED", ["UNHANDLED"]),
    ('["UNHANDLED"]', ["UNHANDLED"]),

    # Test ALL format variations
    ("ALL", ["ALL"]),
    ('["ALL"]', ["ALL"]),

    # Test specific exceptions format variations
    ("ValueError", ["ValueError"]),
    ("ValueError,TypeError", ["ValueError", "TypeError"]),
    ('["ValueError", "TypeError"]', ["ValueError", "TypeError"]),

    # Test comma formats with spaces
    ("ValueError, TypeError", ["ValueError", "TypeError"]),
    ("ValueError,TypeError,CustomError", ["ValueError", "TypeError"]),
])
def test_handled_exceptions_parsing(env_value: str, expected: List[str]):
    """Test different formats for handled_exceptions setting."""
    # Parse JSON if it looks like JSON
    if env_value.startswith('['):
        try:
            value = json.loads(env_value)
        except json.JSONDecodeError:
            value = env_value
    else:
        value = env_value

    settings = Settings(
        openai_api_key="test-key",
        handled_exceptions=value
    )
    assert settings.handled_exceptions == expected

@pytest.mark.parametrize("env_value,expected", [
    # Test single value
    ("KeyboardInterrupt", ["KeyboardInterrupt"]),

    # Test multiple values
    ("KeyboardInterrupt,SystemExit", ["KeyboardInterrupt", "SystemExit"]),
    ('["KeyboardInterrupt", "SystemExit"]', ["KeyboardInterrupt", "SystemExit"]),

    # Test with spaces
    ("KeyboardInterrupt, SystemExit", ["KeyboardInterrupt", "SystemExit"]),
])
def test_ignore_exceptions_parsing(env_value: str, expected: List[str]):
    """Test different formats for ignore_exceptions setting."""
    # Parse JSON if it looks like JSON
    if env_value.startswith('['):
        try:
            value = json.loads(env_value)
        except json.JSONDecodeError:
            value = env_value
    else:
        value = env_value

    settings = Settings(
        openai_api_key="test-key",
        ignore_exceptions=value
    )
    assert settings.ignore_exceptions == expected

@pytest.mark.parametrize("env_value,expected", [
    # Test empty handlers
    ("{}", {}),

    # Test single handler
    ('{"ValueError": "Custom prompt"}', {"ValueError": "Custom prompt"}),

    # Test multiple handlers
    (
        '{"ValueError": "Custom prompt", "TypeError": "Another prompt"}',
        {"ValueError": "Custom prompt", "TypeError": "Another prompt"}
    ),

    # Test multiline prompts
    ('''
    {
        "ValueError": "Line 1\\nLine 2",
        "TypeError": "Multiple\\nLines\\nHere"
    }
    ''', {
        "ValueError": "Line 1\nLine 2",
        "TypeError": "Multiple\nLines\nHere"
    }),
])
def test_custom_handlers_parsing(env_value: str, expected: Dict[str, str]):
    """Test different formats for custom_handlers setting."""
    # Parse JSON string to dict
    try:
        value = json.loads(env_value)
    except json.JSONDecodeError:
        value = {}

    settings = Settings(
        openai_api_key="test-key",
        custom_handlers=value
    )
    assert settings.custom_handlers == expected

def test_default_values():
    """Test default values when no environment variables are set."""
    settings = Settings(openai_api_key="test-key")
    assert settings.handled_exceptions == ["UNHANDLED"]
    assert settings.ignore_exceptions == ["KeyboardInterrupt", "SystemExit"]
    assert settings.custom_handlers == {}
    assert settings.llm_model == "gpt-4"
    assert settings.temperature == 0.2

def test_required_api_key():
    """Test that API key is required."""
    with pytest.raises(Exception):
        Settings()

def test_complete_configuration():
    """Test a complete configuration with all settings."""
    settings = Settings(
        openai_api_key="test-key",
        handled_exceptions=["ValueError", "TypeError"],  # Pass as list
        ignore_exceptions=["KeyboardInterrupt"],  # Pass as list
        custom_handlers={"ValueError": "Custom prompt"},  # Pass as dict
        llm_model="gpt-3.5-turbo",
        temperature=0.5
    )

    assert settings.handled_exceptions == ["ValueError", "TypeError"]
    assert settings.ignore_exceptions == ["KeyboardInterrupt"]
    assert settings.custom_handlers == {"ValueError": "Custom prompt"}
    assert settings.llm_model == "gpt-3.5-turbo"
    assert settings.temperature == 0.5

@pytest.mark.parametrize("handled,ignored,should_handle", [
    (["ALL"], ["KeyboardInterrupt"], True),  # ALL should handle everything except ignored
    (["UNHANDLED"], ["ValueError"], False),  # UNHANDLED should respect ignored
    (["ValueError"], ["ValueError"], False),  # Ignored takes precedence
    (["ValueError", "TypeError"], ["KeyboardInterrupt"], True),  # Should handle specific exceptions
])
def test_exception_handling_logic(handled: List[str], ignored: List[str], should_handle: bool):
    """Test the logic of exception handling with different configurations."""
    settings = Settings(
        openai_api_key="test-key",
        handled_exceptions=handled,
        ignore_exceptions=ignored
    )

    assert settings.handled_exceptions == handled
    assert settings.ignore_exceptions == ignored

def test_environment_variable_loading(monkeypatch):
    """Test loading settings from environment variables."""
    # Test with environment variables
    monkeypatch.setenv("LLM_CATCHER_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_CATCHER_HANDLED_EXCEPTIONS", '["UNHANDLED"]')  # Use JSON format
    monkeypatch.setenv("LLM_CATCHER_IGNORE_EXCEPTIONS", '["KeyboardInterrupt", "SystemExit"]')  # Use JSON format
    monkeypatch.setenv("LLM_CATCHER_CUSTOM_HANDLERS", '{"ValueError": "Custom prompt"}')

    settings = Settings()
    assert settings.openai_api_key == "test-key"
    assert settings.handled_exceptions == ["UNHANDLED"]
    assert settings.ignore_exceptions == ["KeyboardInterrupt", "SystemExit"]
    assert settings.custom_handlers == {"ValueError": "Custom prompt"}

@pytest.mark.parametrize("invalid_value", [
    "INVALID",  # Invalid special handler
    "NotAnException",  # Non-existent exception
    "[InvalidJSON",  # Malformed JSON
    "FakeError",  # Non-existent exception
    "CustomError",  # Custom exception not in valid list
])
def test_invalid_handled_exceptions(invalid_value):
    """Test handling of invalid handled_exceptions values."""
    settings = Settings(
        openai_api_key="test-key",
        handled_exceptions=invalid_value
    )
    # Should fall back to default for invalid values
    assert settings.handled_exceptions == ["UNHANDLED"]

def test_invalid_custom_handlers():
    """Test handling of invalid custom_handlers values."""
    settings = Settings(
        openai_api_key="test-key",
        custom_handlers="{invalid_json"
    )
    # Should fall back to empty dict
    assert settings.custom_handlers == {}

def test_all_vs_unhandled_behavior():
    """Test the difference between ALL and UNHANDLED modes."""
    # Create a custom exception and handler
    class CustomError(Exception):
        pass

    def custom_handler(exc: CustomError):
        return True

    # Test ALL mode
    settings_all = Settings(
        openai_api_key="test-key",
        handled_exceptions=["ALL"]
    )
    assert not settings_all.handle_unhandled_only
    assert "ALL" in settings_all.handled_exceptions

    # Test UNHANDLED mode
    settings_unhandled = Settings(
        openai_api_key="test-key",
        handled_exceptions=["UNHANDLED"]
    )
    assert settings_unhandled.handle_unhandled_only
    assert "UNHANDLED" in settings_unhandled.handled_exceptions

@pytest.mark.parametrize("temp,expected", [
    (0.0, 0.0),
    (1.0, 1.0),
    (0.5, 0.5),
    (-1, 0.0),  # Should clamp to 0
    (1.5, 1.0), # Should clamp to 1
])
def test_temperature_validation(temp, expected):
    """Test temperature is properly validated and clamped."""
    settings = Settings(
        openai_api_key="test-key",
        temperature=temp
    )
    assert settings.temperature == expected

@pytest.mark.parametrize("model", [
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-4-1106-preview",
])
def test_valid_models(model):
    """Test valid model names are accepted."""
    settings = Settings(
        openai_api_key="test-key",
        llm_model=model
    )
    assert settings.llm_model == model

def test_invalid_model_fallback():
    """Test invalid model falls back to default."""
    settings = Settings(
        openai_api_key="test-key",
        llm_model="invalid-model"
    )
    assert settings.llm_model == "gpt-4"  # Default

def test_settings_inheritance():
    """Test that settings properly inherit and override defaults."""
    # Create base settings
    base = Settings(openai_api_key="test-key")

    # Create settings that override some values
    override = Settings(
        openai_api_key="new-key",
        temperature=0.8,
        # Don't override other values
    )

    # Check inheritance
    assert override.llm_model == base.llm_model
    assert override.handled_exceptions == base.handled_exceptions
    assert override.ignore_exceptions == base.ignore_exceptions

    # Check overrides
    assert override.openai_api_key != base.openai_api_key
    assert override.temperature != base.temperature