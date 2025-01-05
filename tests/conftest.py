import warnings
import pytest
import os

def pytest_configure(config):
    """Configure pytest to ignore specific warnings."""
    # Set Jupyter environment variable
    os.environ["JUPYTER_PLATFORM_DIRS"] = "1"

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*platformdirs.*")
    warnings.filterwarnings("ignore", message=".*Support for class-based.*")
    warnings.filterwarnings("ignore", category=UserWarning)

    # Specifically for Pydantic V2 warnings
    warnings.filterwarnings("ignore",
                          message=".*Support for class-based `config` is deprecated.*",
                          category=DeprecationWarning)