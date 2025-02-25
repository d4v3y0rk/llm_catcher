from .settings import get_settings
from loguru import logger
from openai import AsyncOpenAI, OpenAI
from ollama import Client, AsyncClient
import traceback
import os
import sys
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
import asyncio

P = ParamSpec('P')
T = TypeVar('T')


class LLMExceptionDiagnoser:
    """Diagnoses exceptions using LLM."""

    def __init__(self, settings=None, global_handler: bool = True):
        """Initialize the diagnoser with settings.

        Args:
            settings: Optional settings object to override defaults
            global_handler: Whether to install global exception handler (default: True)
        """
        logger.info("Initializing LLM Exception Diagnoser")

        if settings:
            logger.info("Using provided settings object")
            self.settings = settings
        else:
            # Log where settings are coming from
            logger.info("Loading settings from environment/config files...")
            self.settings = get_settings()

        # Initialize the appropriate client based on the provider
        if self.settings.provider == "openai":
            logger.info(f"Using OpenAI provider with model: {self.settings.llm_model}")
            self.async_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self.sync_client = OpenAI(api_key=self.settings.openai_api_key)
        elif self.settings.provider == "ollama":
            logger.info(f"Using Ollama provider with model: {self.settings.llm_model}")
            try:
                self.async_client = AsyncClient()
                self.sync_client = Client()
            except Exception as e:
                logger.error(f"Failed to initialize Ollama client: {str(e)}")
                raise
        else:
            raise ValueError(f"Unsupported provider: {self.settings.provider}")

        # Log final configuration (excluding sensitive data)
        logger.info(
            f"Configuration: provider={self.settings.provider}, "
            f"model={self.settings.llm_model}, "
            f"temperature={self.settings.temperature}"
        )

        if global_handler:
            self.install_global_handler()

    def install_global_handler(self):
        """Install global exception handler using sys.excepthook."""
        original_excepthook = sys.excepthook

        @wraps(sys.excepthook)
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            """Custom exception hook that diagnoses before printing."""
            try:
                diagnosis = self.diagnose(exc_value)
                # print("\nLLM Diagnosis:", file=sys.stderr)
                print(diagnosis, file=sys.stderr)
                # Don't call the original excepthook if we successfully diagnosed
                return
            except Exception as e:
                logger.error(f"Error in global exception handler: {str(e)}")
                # Only call original excepthook if our diagnosis failed
                original_excepthook(exc_type, exc_value, exc_traceback)

        sys.excepthook = custom_excepthook

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
            "Format your response as a concise paragraph that includes the pertinant file name (do not include the full path), "
            "explanation, and fix. If file and line information is available, always reference it."
        )

    def _log_debug_info(self, error: Exception):
        """Log debug information if DEBUG environment variable is set."""
        if os.getenv("DEBUG"):
            logger.debug(f"Provider: {self.settings.provider}")
            logger.debug(f"Diagnosing error: {error}")
            logger.debug(f"Using model: {self.settings.llm_model}")

    async def async_diagnose(self, error: Exception, formatted: bool = True) -> str:
        """Diagnose an exception using LLM (async version)."""
        try:
            logger.info(f"Diagnosing error with {self.settings.provider}")
            self._log_debug_info(error)
            message = {"role": "user", "content": self._get_prompt(error)}

            if self.settings.provider == "openai":
                response = await self.async_client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[message],
                    temperature=self.settings.temperature,
                )
                diagnosis = response.choices[0].message.content.strip()
            elif self.settings.provider == "ollama":
                response = await self.async_client.chat(
                    model=self.settings.llm_model,
                    messages=[message]
                )
                diagnosis = response.message.content.strip()

            if formatted:
                # Format the diagnosis with clear boundaries
                return "\n" + \
                    "="*80 + "\n" + \
                    "LLM DIAGNOSIS\n" + \
                    "="*80 + "\n" + \
                    f"{diagnosis}\n" + \
                    "="*80 + "\n"
            else:
                return diagnosis

        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"

    def diagnose(self, error: Exception, formatted: bool = True) -> str:
        """Diagnose an exception using LLM (sync version)."""
        try:
            logger.info(f"Diagnosing error with {self.settings.provider}")
            self._log_debug_info(error)
            message = {"role": "user", "content": self._get_prompt(error)}

            if self.settings.provider == "openai":
                response = self.sync_client.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=[message],
                    temperature=self.settings.temperature,
                )
                diagnosis = response.choices[0].message.content.strip()
            elif self.settings.provider == "ollama":
                response = self.sync_client.chat(
                    model=self.settings.llm_model,
                    messages=[message]
                )
                diagnosis = response.message.content.strip()

            if formatted:
                # Format the diagnosis with clear boundaries
                return "\n" + \
                    "="*80 + "\n" + \
                    "LLM DIAGNOSIS\n" + \
                    "="*80 + "\n" + \
                    f"{diagnosis}\n" + \
                    "="*80 + "\n"
            else:
                return diagnosis

        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"

    def catch(self, func: Callable[P, T]) -> Callable[P, T]:
        """Decorator to catch and diagnose exceptions in a function.

        Example:
            @diagnoser.catch
            def my_function():
                # This function's exceptions will be diagnosed
                result = 1 / 0
        """
        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                diagnosis = self.diagnose(e)
                print(diagnosis, file=sys.stderr)
                raise  # Re-raise the exception after diagnosis

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                diagnosis = await self.async_diagnose(e)
                print(diagnosis, file=sys.stderr)
                raise  # Re-raise the exception after diagnosis

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
