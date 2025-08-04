from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from tests.conftest import Table

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TableTestTable(Table):
    """Test table for check table consistency."""

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)


class TestTableTest:
    """Test cases for the table consistency."""

    async def test_create_record(self, session: "AsyncSession") -> None:
        """Test if record can be created in the table."""

        instance: TableTestTable = TableTestTable(name="Test Item", email="test@example.com")
        session.add(instance)
        await session.commit()

        assert instance.id is not None
        assert instance.name == "Test Item"
        assert instance.email == "test@example.com"

    async def test_table_fields_consistency(self, session: "AsyncSession") -> None:
        """Test if table has all fields defined in mixins."""

        record: TableTestTable = TableTestTable(name="Test Item", email="test@example.com")
        session.add(record)
        await session.commit()

        instance: TableTestTable | None = (
            await session.execute(
                statement=select(TableTestTable).where(TableTestTable.id == record.id),
            )
        ).scalar()

        assert instance is not None
        assert instance.id is not None
        assert isinstance(instance.id, UUID)
        assert instance.name == "Test Item"
        assert instance.email == "test@example.com"
        assert instance.updated_at is not None
        assert instance.created_at is not None
