from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Dict, List
from ..diagnoser import LLMExceptionDiagnoser
from loguru import logger
import sys

class BaseExceptionHandler(ABC):
    def __init__(self, diagnoser: LLMExceptionDiagnoser, settings: Optional[Dict[str, Any]] = None):
        self.diagnoser = diagnoser
        self.settings = settings or {}

        # Get settings values directly from attributes if it's a Settings object
        if hasattr(settings, 'handled_exceptions'):
            self.handled_exceptions = self._parse_exceptions(settings.handled_exceptions)
            self.ignore_exceptions = self._parse_exceptions(settings.ignore_exceptions)
            self.custom_handlers = settings.custom_handlers
            self.handle_unhandled_only = settings.handle_unhandled_only
        else:
            # Fallback to dictionary access for dict settings
            self.handled_exceptions = self._parse_exceptions(
                settings.get("handled_exceptions", ["Exception"]) if settings else ["Exception"]
            )
            self.ignore_exceptions = self._parse_exceptions(
                settings.get("ignore_exceptions", ["KeyboardInterrupt"]) if settings else ["KeyboardInterrupt"]
            )
            self.custom_handlers = settings.get("custom_handlers", {}) if settings else {}
            self.handle_unhandled_only = settings.get("handle_unhandled_only", False) if settings else False

    def _parse_exceptions(self, exceptions) -> List[Type[Exception]]:
        """Parse exception names into actual exception classes."""
        if not exceptions:
            return []

        if isinstance(exceptions, str):
            exceptions = [exceptions]

        result = []
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

        for exc in exceptions:
            if exc == "ALL":
                result.append(Exception)
            elif exc == "UNHANDLED":
                self.handle_unhandled_only = True
                result.append(Exception)
            else:
                # First try the builtin exceptions map
                if exc in builtin_exceptions:
                    result.append(builtin_exceptions[exc])
                else:
                    # Fallback to eval if not found in map
                    try:
                        exc_class = eval(exc)
                        if isinstance(exc_class, type) and issubclass(exc_class, Exception):
                            result.append(exc_class)
                    except (NameError, TypeError):
                        logger.warning(f"Invalid exception type: {exc}")

        return result

    def should_handle(self, exc: Exception) -> bool:
        """Determine if the exception should be handled."""
        if any(isinstance(exc, ignored) for ignored in self.ignore_exceptions):
            return False
        return any(isinstance(exc, handled) for handled in self.handled_exceptions)

    def get_custom_prompt(self, exc: Exception) -> Optional[str]:
        """Get custom prompt for exception if configured."""
        exc_name = exc.__class__.__name__
        return self.custom_handlers.get(exc_name)

    @abstractmethod
    async def handle_exception(self, exc: Exception, **kwargs) -> Any:
        """Handle the exception and return appropriate response."""
        pass