from pydantic_settings import BaseSettings
from typing import List, Dict, Any, Union
from loguru import logger
import json
import os
from pathlib import Path
from pydantic import Field, ValidationError, validator

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
    """Settings for LLM Catcher."""

    openai_api_key: str = Field(default=None)
    llm_model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.2)
    handled_exceptions: Union[str, List[str]] = Field(default=["UNHANDLED"])
    ignore_exceptions: Union[str, List[str]] = Field(default=["SystemExit"])
    custom_handlers: Union[str, Dict[str, str]] = Field(default_factory=dict)
    handle_unhandled_only: bool = Field(default=False)
    include_traceback: bool = Field(default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._process_settings()

    def _process_settings(self):
        """Process and validate settings after initialization."""
        # Convert string to list for exceptions
        if isinstance(self.handled_exceptions, str):
            self.handled_exceptions = [self.handled_exceptions]
        if isinstance(self.ignore_exceptions, str):
            self.ignore_exceptions = [self.ignore_exceptions]

        # Validate temperature
        if self.temperature < 0:
            self.temperature = 0.0
        elif self.temperature > 1:
            self.temperature = 1.0

        # Validate model
        valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"]
        if self.llm_model not in valid_models:
            self.llm_model = "gpt-4"

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

    @validator('handled_exceptions', 'ignore_exceptions', pre=True)
    def parse_exceptions(cls, v):
        if isinstance(v, str):
            if ',' in v:
                return [x.strip() for x in v.split(',')]
            return [v]
        return v

    @validator('temperature', pre=True)
    def validate_temperature(cls, v):
        """Validate and clamp temperature between 0 and 1."""
        if isinstance(v, (int, float)):
            if v < 0:
                return 0.0
            if v > 1:
                return 1.0
        return v

    @validator('custom_handlers', pre=True)
    def parse_custom_handlers(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v

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
        logger.debug("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        logger.error("Make sure LLM_CATCHER_OPENAI_API_KEY is set in your environment")
        raise