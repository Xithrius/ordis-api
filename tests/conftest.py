from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from api.application import get_app
from api.database.dependencies import get_db_session
from api.database.utils import create_database, drop_database


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:  # pyright: ignore[reportUnusedFunction]
    """
    Create engine and databases.

    :yield: new engine.
    """
    from api.database.meta import meta
    from api.database.models import load_all_models

    load_all_models()

    postgres = PostgresContainer("postgres:16-alpine", driver="psycopg")
    _ = postgres.start()

    url = postgres.get_connection_url()

    await create_database(url)

    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database(url)
        postgres.stop()


@pytest.fixture
async def dbsession(_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(dbsession: AsyncSession) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession

    return application


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :param anyio_backend: the anyio backend
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=5.0) as ac:
        yield ac
