import openai
from typing import Optional, Type
from pydantic import BaseModel
from .settings import get_settings
from loguru import logger
from openai import AsyncOpenAI

class LLMExceptionDiagnoser:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize the diagnoser with optional override settings.
        If not provided, will use settings from environment.
        """
        logger.info("Initializing LLM Exception Diagnoser")
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model or self.settings.llm_model
        self.temperature = self.settings.temperature
        logger.debug(f"Using model: {self.model}")

    async def diagnose(
        self,
        stack_trace: str,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        request_data: Optional[dict] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Diagnose an exception using LLM."""
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
                schema_info += f"\nActual Request Data:\n{request_data}"

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
            logger.debug(f"Diagnosis: {diagnosis}")
            return diagnosis
        except Exception as e:
            logger.error(f"Error during diagnosis: {str(e)}")
            return f"Failed to contact LLM for diagnosis. Error: {str(e)}"