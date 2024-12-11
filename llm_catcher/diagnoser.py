import openai
from typing import Optional, Type
from pydantic import BaseModel
from .settings import get_settings
from loguru import logger
from openai import AsyncOpenAI

class LLMExceptionDiagnoser:
    def __init__(self, settings=None, api_key: str | None = None, model: str | None = None):
        """
        Initialize the diagnoser with either settings object or individual parameters.

        Args:
            settings: Settings object (takes precedence if provided)
            api_key: Optional API key override
            model: Optional model override
        """
        logger.info("Initializing LLM Exception Diagnoser")

        if settings:
            self.settings = settings
            self.api_key = settings.openai_api_key  # For backward compatibility
        else:
            self.settings = get_settings()
            if api_key:
                self.settings.openai_api_key = api_key
                self.api_key = api_key  # For backward compatibility
            else:
                self.api_key = self.settings.openai_api_key  # For backward compatibility
            if model:
                self.settings.llm_model = model

        # Initialize OpenAI client with API key from settings
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            organization=None  # Add this if needed for project API keys
        )

        self.model = self.settings.llm_model
        self.temperature = self.settings.temperature
        logger.debug(f"Using model: {self.model}")

    async def diagnose(
        self,
        exc: Exception,
        stack_trace: str,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        request_data: Optional[dict] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Diagnose an exception using LLM.

        Args:
            exc: The exception to diagnose
            stack_trace: The stack trace string
            request_model: Optional request model schema
            response_model: Optional response model schema
            request_data: Optional request data for context
            custom_prompt: Optional custom prompt to use

        Returns:
            str: The diagnosis from the LLM
        """
        try:
            logger.info("Starting diagnosis...")
            schema_info = ""
            if request_model:
                logger.debug(f"Including request model: {request_model.__name__}")
                schema_info += f"\nRequest Schema:\n{request_model.model_json_schema()}"
            if response_model:
                logger.debug(f"Including response model: {response_model.__name__}")
                schema_info += f"\nResponse Schema:\n{response_model.model_json_schema()}"
            if request_data:
                logger.debug("Including request data")

            logger.debug("Preparing prompt for LLM")
            prompt = custom_prompt or (
                "I received the following stack trace and schema information from a Python application. "
                "Please analyze the error and provide a diagnosis that includes:\n"
                "1. The specific file and line number where the error occurred\n"
                "2. A clear explanation of what went wrong\n"
                "3. Suggestions for fixing the issue\n\n"
                f"Stack Trace:\n{stack_trace}\n"
                f"{schema_info}\n\n"
                "Format your response as a concise paragraph that includes the file location, "
                "explanation, and fix. If file and line information is available, always reference it."
            )

            logger.info("Sending request to OpenAI...")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            diagnosis = response.choices[0].message.content.strip()
            logger.info("Received diagnosis from OpenAI")
            return diagnosis
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"