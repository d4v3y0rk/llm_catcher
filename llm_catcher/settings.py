from pydantic_settings import BaseSettings
from typing import List, Dict, Any, Union
from loguru import logger
import json
import os
from pathlib import Path
from pydantic import Field, ValidationError

def load_env_file(env_file: str = '.env') -> None:
    """Load environment variables from file."""
    try:
        env_path = Path(env_file)
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    except Exception as e:
        logger.warning(f"Error loading .env file: {str(e)}")

class Settings(BaseSettings):
    """Settings for LLM Catcher with sensible defaults."""

    # Required setting - no default for API key
    openai_api_key: str = Field(..., description="OpenAI API key is required")

    # Optional settings with defaults
    llm_model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.2)
    handled_exceptions: Union[str, List[str]] = Field(default=["UNHANDLED"])
    ignore_exceptions: Union[str, List[str]] = Field(default=["KeyboardInterrupt", "SystemExit"])
    custom_handlers: Union[str, Dict[str, str]] = Field(default_factory=dict)
    handle_unhandled_only: bool = Field(default=False)

    def __init__(self, **kwargs):
        # Check for required API key
        if not kwargs.get('openai_api_key') and not os.environ.get('LLM_CATCHER_OPENAI_API_KEY'):
            raise ValidationError([{
                'loc': ('openai_api_key',),
                'msg': 'OpenAI API key is required',
                'type': 'value_error.missing'
            }])

        super().__init__(**kwargs)
        self._process_settings()

    def _process_settings(self):
        """Process and validate settings after initialization."""
        # Handle temperature bounds
        self.temperature = max(0.0, min(1.0, self.temperature))

        # Validate model
        valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"]
        if self.llm_model not in valid_models:
            self.llm_model = "gpt-4"

        # Process handled exceptions
        if isinstance(self.handled_exceptions, str):
            if self.handled_exceptions in ["ALL", "UNHANDLED"]:
                self.handled_exceptions = [self.handled_exceptions]
            else:
                try:
                    # Try JSON first
                    parsed = json.loads(self.handled_exceptions)
                    if isinstance(parsed, list):
                        self.handled_exceptions = parsed
                    else:
                        self.handled_exceptions = [x.strip() for x in self.handled_exceptions.split(",")]
                except json.JSONDecodeError:
                    self.handled_exceptions = [x.strip() for x in self.handled_exceptions.split(",")]

        # Process ignore exceptions
        if isinstance(self.ignore_exceptions, str):
            try:
                # Try JSON first
                parsed = json.loads(self.ignore_exceptions)
                if isinstance(parsed, list):
                    self.ignore_exceptions = parsed
                else:
                    self.ignore_exceptions = [x.strip() for x in self.ignore_exceptions.split(",")]
            except json.JSONDecodeError:
                self.ignore_exceptions = [x.strip() for x in self.ignore_exceptions.split(",")]

        # Process custom handlers
        if isinstance(self.custom_handlers, str):
            try:
                self.custom_handlers = json.loads(self.custom_handlers)
            except json.JSONDecodeError:
                self.custom_handlers = {}
        elif not isinstance(self.custom_handlers, dict):
            self.custom_handlers = {}

        # Validate handled exceptions
        valid_special = ["ALL", "UNHANDLED"]
        valid_exceptions = [
            "ValueError", "TypeError", "AttributeError", "KeyError",
            "IndexError", "ZeroDivisionError", "FileNotFoundError",
            "ImportError", "RuntimeError", "Exception"
        ]
        valid = [x for x in self.handled_exceptions if x in valid_special + valid_exceptions]
        self.handled_exceptions = valid if valid else ["UNHANDLED"]

        # Set unhandled flag
        self.handle_unhandled_only = "UNHANDLED" in self.handled_exceptions

    class Config:
        env_prefix = "LLM_CATCHER_"
        case_sensitive = False
        env_file = None  # Don't load .env file automatically

def get_settings() -> Settings:
    """Get settings from environment variables with defaults."""
    try:
        # Try loading .env file first
        load_env_file()

        # Then create settings from environment
        settings = Settings()
        logger.debug(f"Loaded settings: {settings.dict()}")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        logger.error("Make sure LLM_CATCHER_OPENAI_API_KEY is set in your environment")
        raise