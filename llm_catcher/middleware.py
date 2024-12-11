from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from .handlers.fastapi_handler import FastAPIExceptionHandler
from .diagnoser import LLMExceptionDiagnoser
from .settings import get_settings
from loguru import logger

class LLMCatcherMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        api_key: str | None = None,
        model: str | None = None,
        settings: dict | None = None
    ):
        super().__init__(app)
        logger.info("Initializing LLM Catcher middleware...")
        diagnoser = LLMExceptionDiagnoser(api_key=api_key, model=model)
        self.handler = FastAPIExceptionHandler(diagnoser, settings)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            if any(isinstance(exc, ignored) for ignored in self.handler.ignore_exceptions):
                raise

            # Check if we should only handle unhandled exceptions
            if hasattr(self.handler, 'handle_unhandled_only'):
                # Check if there's an existing handler
                exception_handler = request.app.exception_handlers.get(
                    type(exc)
                ) or request.app.exception_handlers.get(Exception)

                if exception_handler:
                    raise  # Let the existing handler handle it

            # Handle the exception if it matches our criteria
            if any(isinstance(exc, handled) for handled in self.handler.handled_exceptions):
                return await self.handler.handle_exception(exc, request=request)

            raise  # Re-raise if we shouldn't handle it

def add_exception_diagnoser(app: FastAPI, api_key: str | None = None, model: str | None = None):
    """
    Add exception diagnoser middleware to FastAPI app.
    Optional parameters override environment settings.
    """
    app.add_middleware(LLMCatcherMiddleware, api_key=api_key, model=model)