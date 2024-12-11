from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from .handlers.fastapi_handler import FastAPIExceptionHandler
from .diagnoser import LLMExceptionDiagnoser
from .settings import get_settings
from loguru import logger
import anyio

class LLMCatcherMiddleware(BaseHTTPMiddleware):
    """Middleware that catches exceptions and diagnoses them using LLM."""

    def __init__(
        self,
        app: FastAPI,
        api_key: str | None = None,
        model: str | None = None,
        settings: dict | None = None,
    ):
        """Initialize the middleware with optional API key and model."""
        super().__init__(app)
        logger.info("Initializing LLM Catcher middleware...")
        self.settings = settings or {}
        self.diagnoser = LLMExceptionDiagnoser(api_key=api_key, model=model, settings=self.settings)
        self.handler = FastAPIExceptionHandler(self.diagnoser, settings=self.settings)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle the request and catch any exceptions."""
        try:
            return await call_next(request)
        except (anyio.ExceptionGroup, Exception) as exc:
            # If it's an ExceptionGroup, extract the original exception
            if isinstance(exc, anyio.ExceptionGroup):
                exc = exc.exceptions[0]

            # First check if this is an ignored exception
            if any(isinstance(exc, ignored) for ignored in self.handler.ignore_exceptions):
                logger.debug(f"Ignoring exception type: {type(exc).__name__}")
                raise exc from None

            # Then check if we should handle it
            if self.handler.handle_unhandled_only:
                # Check if there's an existing handler
                exception_handler = request.app.exception_handlers.get(
                    type(exc)
                )
                if exception_handler:
                    raise exc from None

            # Handle the exception if it matches our criteria
            if any(isinstance(exc, handled) for handled in self.handler.handled_exceptions):
                return await self.handler.handle_exception(exc, request=request)

            raise exc from None

def add_exception_diagnoser(app: FastAPI, api_key: str | None = None, model: str | None = None):
    """Add exception diagnoser middleware to FastAPI app."""
    settings = get_settings()
    if api_key:
        settings.openai_api_key = api_key
    if model:
        settings.llm_model = model
    app.add_middleware(LLMCatcherMiddleware, settings=settings)