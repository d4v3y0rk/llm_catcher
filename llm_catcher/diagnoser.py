from .settings import get_settings
from loguru import logger
from openai import AsyncOpenAI, OpenAI
import traceback

class LLMExceptionDiagnoser:
    """Diagnoses exceptions using LLM."""

    def __init__(self, settings=None, api_key: str | None = None, model: str | None = None):
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

        # Initialize both sync and async clients
        self.async_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.sync_client = OpenAI(api_key=self.settings.openai_api_key)
        logger.debug(f"Using model: {self.settings.llm_model}")

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
            response = await self.async_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[{"role": "user", "content": self._get_prompt(error)}],
                temperature=self.settings.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"

    def diagnose(self, error: Exception) -> str:
        """Diagnose an exception using LLM (sync version)."""
        try:
            response = self.sync_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[{"role": "user", "content": self._get_prompt(error)}],
                temperature=self.settings.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"


