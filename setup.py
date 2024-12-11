from setuptools import setup, find_packages

setup(
    name="llm-catcher",
    version="0.2.6",
    description="A FastAPI middleware that uses LLMs to diagnose API errors",
    author="Dave York",
    author_email="dave.york@me.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "requests>=2.26.0",
        "uvicorn>=0.15.0",
        "openai>=0.27.0",
        "python-dotenv>=0.19.0",
        "loguru>=0.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
            "httpx>=0.23.0",
            "black>=22.3.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.8",
)
