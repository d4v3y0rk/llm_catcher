import asyncio
from llm_catcher import LLMExceptionDiagnoser

async def main():
    diagnoser = LLMExceptionDiagnoser()
    try:
        1/0  # Cause a zero division error
    except Exception as e:
        print(await diagnoser.diagnose(e))

if __name__ == "__main__":
    asyncio.run(main())