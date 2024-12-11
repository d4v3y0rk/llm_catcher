from pydantic_settings import BaseSettings
from loguru import logger
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Settings for LLM Catcher."""
    openai_api_key: str = Field(default=None)
    llm_model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.2)

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate and clamp temperature between 0 and 1."""
        if isinstance(v, (int, float)):
            return max(0.0, min(1.0, float(v)))
        return v

    @field_validator('llm_model')
    @classmethod
    def validate_model(cls, v):
        """Validate the model name."""
        valid_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
        if v not in valid_models:
            logger.warning(f"Invalid model {v}, falling back to gpt-4o-mini")
            return "gpt-4o-mini"
        return v

    class Config:
        env_prefix = "LLM_CATCHER_"
        env_file = '.env'
        env_file_encoding = 'utf-8'

def get_settings() -> Settings:
    """Get settings from environment variables."""
    try:
        settings = Settings()
        logger.debug("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        logger.error("Make sure LLM_CATCHER_OPENAI_API_KEY is set in your environment")
        raise