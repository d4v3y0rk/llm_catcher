from .settings import get_settings
from loguru import logger
from openai import AsyncOpenAI, OpenAI
from ollama import Client, AsyncClient
import traceback

class LLMExceptionDiagnoser:
    """Diagnoses exceptions using LLM."""

    def __init__(self, settings=None, api_key: str | None = None, model: str | None = None, provider: str | None = None):
        """Initialize the diagnoser with settings or individual parameters."""
        logger.info("Initializing LLM Exception Diagnoser")

        if settings:
            self.settings = settings
        else:
            self.settings = get_settings()
            if api_key:
                self.settings.openai_api_key = api_key
            if model:
                self.settings.llm_model = model
            if provider:
                self.settings.provider = provider

        # Initialize the appropriate client based on the provider
        if self.settings.provider == "openai":
            self.async_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self.sync_client = OpenAI(api_key=self.settings.openai_api_key)
        elif self.settings.provider == "ollama":
            self.async_client = AsyncClient()
            self.sync_client = Client()
        else:
            raise ValueError(f"Unsupported provider: {self.settings.provider}")

    @property
    def llm_model(self) -> str:
        """Get current LLM model."""
        return self.settings.llm_model

    @llm_model.setter
    def llm_model(self, model: str):
        """Set LLM model."""
        self.settings.llm_model = model
        logger.debug(f"Model updated to: {model}")

    @property
    def temperature(self) -> float:
        """Get current temperature setting."""
        return self.settings.temperature

    @temperature.setter
    def temperature(self, value: float):
        """Set temperature value."""
        self.settings.temperature = value
        logger.debug(f"Temperature updated to: {value}")

    def _get_prompt(self, error: Exception) -> str:
        """Get the diagnosis prompt for an error."""
        stack_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        return (
            "I received the following stack trace from a Python application. "
            "Please analyze the error and provide a diagnosis that includes:\n"
            "1. The specific file and line number where the error occurred\n"
            "2. A clear explanation of what went wrong\n"
            "3. Suggestions for fixing the issue\n\n"
            f"Stack Trace:\n{stack_trace}\n"
            "Format your response as a concise paragraph that includes the file location, "
            "explanation, and fix. If file and line information is available, always reference it."
        )

    async def async_diagnose(self, error: Exception) -> str:
        """Diagnose an exception using LLM (async version)."""
        try:
            logger.info(f"Provider: {self.settings.provider}")
            logger.info(f"Diagnosing error: {error}")
            logger.info(f"Using model: {self.settings.llm_model}")
            message = {"role": "user", "content": self._get_prompt(error)}
            if self.settings.provider == "openai":
                response = await self.async_client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[message],
                    temperature=self.settings.temperature,
                )
                return response.choices[0].message.content.strip()
            elif self.settings.provider == "ollama":
                response = await self.async_client.chat(
                    model=self.settings.llm_model,
                    messages=[message]
                )
                return response.message.content.strip()
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"

    def diagnose(self, error: Exception) -> str:
        """Diagnose an exception using LLM (sync version)."""
        try:
            logger.info(f"Provider: {self.settings.provider}")
            logger.info(f"Diagnosing error: {error}")
            logger.info(f"Using model: {self.settings.llm_model}")
            message = {"role": "user", "content": self._get_prompt(error)}
            if self.settings.provider == "openai":
                response = self.sync_client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[message],
                    temperature=self.settings.temperature,
                )
                return response.choices[0].message.content.strip()
            elif self.settings.provider == "ollama":
                response = self.sync_client.chat(
                    model=self.settings.llm_model,
                    messages=[message]
                )
                return response.message.content.strip()
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"


