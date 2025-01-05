from pydantic_settings import BaseSettings
from loguru import logger
from pydantic import Field, field_validator, model_validator, ValidationInfo
import json

class Settings(BaseSettings):
    """Settings for LLM Catcher."""
    openai_api_key: str | None = Field(default=None)
    llm_model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.2)
    provider: str = Field(default="openai")

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate and clamp temperature between 0 and 1."""
        if isinstance(v, (int, float)):
            return max(0.0, min(1.0, float(v)))
        return v

    @field_validator('llm_model')
    @classmethod
    def validate_model(cls, v, info: ValidationInfo):
        """Validate the model name based on the provider."""
        provider = info.data.get('provider')
        if provider == "openai":
            valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
            if v not in valid_models:
                logger.warning(f"Invalid model {v} for OpenAI, falling back to gpt-4o-mini")
                return "gpt-4o-mini"
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

    class Config:
        env_prefix = "LLM_CATCHER_"
        env_file = '.env'
        env_file_encoding = 'utf-8'

def get_settings() -> Settings:
    """Get settings from environment variables or config file."""
    try:
        # Attempt to load settings from a config file
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            settings = Settings(**config_data)
        logger.debug("Settings loaded successfully from config file")
        return settings
    except FileNotFoundError:
        logger.warning("Config file not found, loading settings from environment")
        settings = Settings()
        logger.debug("Settings loaded successfully from environment")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        logger.error("Make sure LLM_CATCHER_OPENAI_API_KEY is set in your environment if using OpenAI")
        raise