import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.database.dependencies import get_session
from src.main import app
from src.models import Base
from src.services import auth_service

load_dotenv(".env.test", override=True)
POSTGRES_TEST_USER = os.getenv("POSTGRES_TEST_USER")
POSTGRES_TEST_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB")
POSTGRES_TEST_PORT = os.getenv("POSTGRES_TEST_PORT")

TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_TEST_USER}:{POSTGRES_TEST_PASSWORD}@localhost:{POSTGRES_TEST_PORT}/{POSTGRES_TEST_DB}"

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth_service, "get_password_hash", lambda p: f"hashed:{p}")
    monkeypatch.setattr(
        auth_service, "verify_password", lambda p, h: h == f"hashed:{p}"
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db() -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session_maker = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_maker() as session:
            yield session

        await transaction.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
