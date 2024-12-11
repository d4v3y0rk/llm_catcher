from .base import BaseExceptionHandler
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
import traceback
from loguru import logger

class FastAPIExceptionHandler(BaseExceptionHandler):
    async def handle_exception(self, exc: Exception, **kwargs) -> JSONResponse:
        request = kwargs.get("request")
        if not request or not isinstance(request, Request):
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "diagnosis": "Request object not provided"}
            )

        try:
            stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

            # Get route information
            route = request.scope.get("route")
            request_model = None
            response_model = None
            request_data = None

            if isinstance(route, APIRoute):
                # Get request model from endpoint parameters
                for param in route.dependant.body_params:
                    if hasattr(param.type_, "model_json_schema"):
                        request_model = param.type_
                response_model = route.response_model

            # Try to get request data regardless of route type
            try:
                request_data = await request.json()
                logger.debug(f"Got request data: {request_data}")
            except Exception as e:
                logger.debug(f"Could not parse request data: {str(e)}")

            # Get custom prompt if configured
            custom_prompt = self.get_custom_prompt(exc)

            diagnosis = await self.diagnoser.diagnose(
                stack_trace,
                request_model=request_model,
                response_model=response_model,
                request_data=request_data,
                custom_prompt=custom_prompt
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "diagnosis": diagnosis,
                    "exception_type": exc.__class__.__name__,
                    "has_schema_info": bool(request_model or response_model)
                }
            )
        except Exception as e:
            logger.error(f"Error in exception handler: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "diagnosis": str(e)}
            )