from setuptools import setup, find_packages

setup(
    name="llm-catcher",
    version="0.4.0",
    description="A Python library that uses LLMs to diagnose and explain exceptions",
    author="Dave York",
    author_email="dave.york@me.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "loguru>=0.6.0",
    ],
    extras_require={
        "fastapi": [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "requests>=2.26.0",
        ],
    },
    python_requires=">=3.8",
)
