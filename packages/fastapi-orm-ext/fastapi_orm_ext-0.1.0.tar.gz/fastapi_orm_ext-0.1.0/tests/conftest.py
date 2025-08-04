from typing import TYPE_CHECKING

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from fastapi_orm_ext.table import TableBase

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncEngine

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class Table(TableBase, DeclarativeBase):
    __abstract__: bool = True


@pytest_asyncio.fixture
async def engine() -> "AsyncGenerator[AsyncEngine]":
    engine: AsyncEngine = create_async_engine(
        url=TEST_DATABASE_URL,
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(fn=Table.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session(engine: "AsyncEngine") -> "AsyncGenerator[AsyncSession]":
    async_session: AsyncSession = AsyncSession(bind=engine, expire_on_commit=False)
    try:
        yield async_session
    finally:
        await async_session.close()
