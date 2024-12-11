from .base import BaseExceptionHandler
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
import traceback
from loguru import logger

class FastAPIExceptionHandler(BaseExceptionHandler):
    """FastAPI-specific exception handler."""

    def __init__(self, diagnoser, settings=None):
        """Initialize the handler with diagnoser and settings."""
        super().__init__(diagnoser, settings)

    async def handle_exception(self, exc: Exception, **kwargs) -> JSONResponse:
        """Handle exception and return FastAPI response."""
        try:
            request = kwargs.get('request')
            custom_prompt = self.get_custom_prompt(exc)

            # Get the full traceback
            stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logger.debug(f"Stack trace: {stack_trace}")

            # Extract request data if available
            request_data = None
            if request and isinstance(request, Request):
                try:
                    request_data = await request.json()
                except:
                    request_data = None

            # Get route models if available
            request_model = None
            response_model = None
            if request and hasattr(request.scope.get('route'), 'endpoint'):
                endpoint = request.scope['route'].endpoint
                if hasattr(endpoint, '__annotations__'):
                    annotations = endpoint.__annotations__
                    request_model = next((v for k, v in annotations.items()
                                      if k != 'return' and isinstance(v, type)), None)
                    response_model = annotations.get('return')

            # Get diagnosis with full context
            diagnosis = await self.diagnoser.diagnose(
                exc,
                stack_trace,
                request_model=request_model,
                response_model=response_model,
                request_data=request_data,
                custom_prompt=custom_prompt
            )

            # Include traceback in response if enabled
            include_traceback = (
                hasattr(self.settings, 'include_traceback') and
                self.settings.include_traceback
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                    "diagnosis": diagnosis,
                    "traceback": stack_trace if include_traceback else None
                }
            )
        except Exception as e:
            logger.error(f"Error in exception handler: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "diagnosis": str(e)}
            )