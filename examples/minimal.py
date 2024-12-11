from llm_catcher import LLMExceptionDiagnoser
from llm_catcher.settings import get_settings
import asyncio
import traceback

async def main():
    diagnoser = LLMExceptionDiagnoser(settings=get_settings())
    try:
        1/0  # Cause a zero division error
    except Exception as e:
        stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(await diagnoser.diagnose(e, stack_trace))

if __name__ == "__main__":
    asyncio.run(main())