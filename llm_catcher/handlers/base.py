from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Dict, List
from ..diagnoser import LLMExceptionDiagnoser
from loguru import logger
import sys

class BaseExceptionHandler(ABC):
    def __init__(self, diagnoser: LLMExceptionDiagnoser, settings: Optional[Dict[str, Any]] = None):
        self.diagnoser = diagnoser
        self.settings = settings or {}
        self.handled_exceptions = self._get_exception_classes(
            self.settings.get("handled_exceptions", ["Exception"])
        )
        self.ignore_exceptions = self._get_exception_classes(
            self.settings.get("ignore_exceptions", [])
        )
        self.custom_handlers = self.settings.get("custom_handlers", {})

    def _get_exception_classes(self, exception_names: list[str]) -> list[Type[Exception]]:
        """Convert exception names to actual exception classes."""
        exceptions = []

        # Handle special cases
        if "ALL" in exception_names:
            return [Exception]  # Will catch all exceptions

        if "UNHANDLED" in exception_names:
            # Return a special marker that the middleware will use
            self.handle_unhandled_only = True
            return [Exception]  # Will be filtered by middleware

        # Normal exception handling
        builtin_exceptions = {
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'AttributeError': AttributeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'RuntimeError': RuntimeError,
            'KeyboardInterrupt': KeyboardInterrupt,
            'SystemExit': SystemExit,
            'FileNotFoundError': FileNotFoundError,
            'ZeroDivisionError': ZeroDivisionError,
            'ImportError': ImportError,
            'NameError': NameError,
            'SyntaxError': SyntaxError,
            'PermissionError': PermissionError,
            'OSError': OSError,
            'IOError': IOError,
            'AssertionError': AssertionError,
        }

        for name in exception_names:
            if name in builtin_exceptions:
                exceptions.append(builtin_exceptions[name])
            else:
                logger.warning(f"Could not find exception class: {name}")

        return exceptions

    def should_handle(self, exc: Exception) -> bool:
        """Determine if the exception should be handled."""
        if any(isinstance(exc, ignored) for ignored in self.ignore_exceptions):
            return False
        return any(isinstance(exc, handled) for handled in self.handled_exceptions)

    def get_custom_prompt(self, exc: Exception) -> Optional[str]:
        """Get custom prompt for specific exception type if configured."""
        for exc_name, prompt in self.custom_handlers.items():
            if exc.__class__.__name__ == exc_name:
                return prompt
        return None

    @abstractmethod
    async def handle_exception(self, exc: Exception, **kwargs) -> Any:
        """Handle the exception and return appropriate response."""
        pass