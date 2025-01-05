from pydantic_settings import BaseSettings
from loguru import logger
from pydantic import Field, field_validator, model_validator, ValidationInfo, ConfigDict
import json
import os
from typing import Dict, Any

class Settings(BaseSettings):
    """Settings for LLM Catcher."""
    model_config = ConfigDict(
        env_prefix="LLM_CATCHER_",
        env_file='.env',
        env_file_encoding='utf-8'
    )

    openai_api_key: str | None = Field(default=None)
    llm_model: str = Field(default="qwen2.5-coder")
    temperature: float | None = Field(default=None)
    provider: str = Field(default="ollama")

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v, info: ValidationInfo):
        """Validate and clamp temperature between 0 and 1 for OpenAI."""
        provider = info.data.get('provider')
        if provider == "openai":
            if isinstance(v, (int, float)):
                return max(0.0, min(1.0, float(v)))
            return 0.2  # Default for OpenAI
        return None  # Not used for Ollama

    @field_validator('llm_model')
    @classmethod
    def validate_model(cls, v, info: ValidationInfo):
        """Validate the model name based on the provider."""
        provider = info.data.get('provider')
        if provider == "openai":
            valid_models = [
                # GPT-4 Series
                "gpt-4", "gpt-4-turbo",
                # GPT-4o Series
                "gpt-4o", "gpt-4o-mini",
                # o1 Series
                "o1", "o1-mini",
                # GPT-3.5 Series
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
            ]
            if v not in valid_models:
                logger.warning(f"Invalid model {v} for OpenAI, falling back to gpt-4")
                return "gpt-4"
        # For Ollama, allow any model name
        return v

    @model_validator(mode='after')
    def check_api_key(cls, values):
        """Ensure API key is provided if using OpenAI."""
        provider = values.provider
        api_key = values.openai_api_key
        if provider == "openai" and not api_key:
            raise ValueError("OpenAI API key must be provided when using OpenAI as the provider.")
        return values

def load_config_file() -> Dict[Any, Any]:
    """Load configuration from JSON file."""
    config_paths = [
        "llm_catcher_config.json",
        "config.json",
        os.path.expanduser("~/.llm_catcher_config.json"),
    ]

    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse config file: {path}")
            except Exception as e:
                logger.warning(f"Error reading config file {path}: {str(e)}")
    return {}

def get_settings() -> Settings:
    """
    Get settings with the following precedence (highest to lowest):
    1. Local config files (./llm_catcher_config.json, ./config.json)
    2. User home config (~/.llm_catcher_config.json)
    3. Environment variables
    4. Default values
    """
    # First check local directory config files
    local_paths = [
        "llm_catcher_config.json",
        "config.json",
    ]

    # Then check home directory
    home_paths = [
        os.path.expanduser("~/.llm_catcher_config.json"),
    ]

    # Try local configs first
    for path in local_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    logger.debug(f"Loaded configuration from {path}")
                    return Settings(**config)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse config file: {path}")
            except Exception as e:
                logger.warning(f"Error reading config file {path}: {str(e)}")

    # Try home directory config
    for path in home_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                    logger.debug(f"Loaded configuration from {path}")
                    return Settings(**config)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse config file: {path}")
            except Exception as e:
                logger.warning(f"Error reading config file {path}: {str(e)}")

    # Finally, fall back to environment variables and defaults
    logger.debug("Using environment variables and defaults")
    return Settings()