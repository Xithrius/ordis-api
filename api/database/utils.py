from sqlalchemy import URL, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from api.settings import settings


async def create_database(url: str | URL | None = None) -> None:
    """Create a database."""
    if url is None:
        url = make_url(str(settings.db_url.with_path("/postgres")))

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.db_base}'",  # noqa: S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{settings.db_base}" ENCODING "utf8" TEMPLATE template1',
            ),
        )
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))


async def drop_database(url: str | URL | None = None) -> None:
    """Drop current database."""
    if url is None:
        url = make_url(str(settings.db_url.with_path("/postgres")))

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{settings.db_base}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{settings.db_base}"'))
