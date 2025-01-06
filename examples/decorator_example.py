from llm_catcher import LLMExceptionDiagnoser
import asyncio
import sqlite3

diagnoser = LLMExceptionDiagnoser()


@diagnoser.catch
def risky_function():
    """This function will raise an error that gets diagnosed."""
    return 1 / 0


@diagnoser.catch
async def async_risky_function():
    """This async function will raise an error that gets diagnosed."""
    import pandas  # noqa: F401, F841
    return True


@diagnoser.catch
def database_error():
    """This will raise a sqlite3.OperationalError."""
    # Try to connect to a database in a non-existent directory
    conn = sqlite3.connect('/nonexistent/directory/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nonexistent_table")


async def main():
    try:
        risky_function()
    except Exception as e:  # noqa: B902, F841
        # don't do anything, the diagnoser will handle it
        pass
    try:
        await async_risky_function()
    except Exception as e:  # noqa: B902, F841
        # don't do anything, the diagnoser will handle it
        pass
    try:
        database_error()
    except Exception as e:  # noqa: B902, F841
        # don't do anything, the diagnoser will handle it
        pass

if __name__ == "__main__":
    asyncio.run(main())
