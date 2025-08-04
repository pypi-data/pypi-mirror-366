from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_orm_ext.errors import ObjectNotFoundError
from fastapi_orm_ext.repository import RepositoryBase
from tests.conftest import Table

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class RepositoryTestTable(Table):
    """Test table for testing repository."""

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=True)


class CreateSchemaTest(BaseModel):
    """Schema for creating a new instance with the repository."""

    id: UUID4 | None = None
    name: str
    email: str | None = None


class UpdateSchemaTest(BaseModel):
    """Schema for updating an existing instance with the repository."""

    name: str | None = None
    email: str | None = None


class RepositoryTest(RepositoryBase[RepositoryTestTable]):
    """Repository for testing repository functionality."""

    model: type[RepositoryTestTable] = RepositoryTestTable
    auto_commit: bool = False
    auto_flush: bool = True


class TestRepository:
    """Test cases for the repository functionality."""

    async def test_create(self, session: "AsyncSession") -> None:
        """Test if a record can be created with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)

        instance: RepositoryTestTable = await repository.create(
            schema=CreateSchemaTest(
                name="Test Item",
                email="test@example.com",
            ),
        )

        assert instance.name == "Test Item"
        assert instance.email == "test@example.com"

    async def test_get(self, session: "AsyncSession") -> None:
        """Test if a record can be retrieved by ID with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)
        id_: UUID4 = uuid4()
        _: RepositoryTestTable = await repository.create(
            schema=CreateSchemaTest(
                id=id_,
                name="Test Item",
                email="test@example.com",
            ),
        )

        instance: RepositoryTestTable | None = await repository.get(id_=id_)

        assert instance is not None
        assert instance.id == id_
        assert instance.name == "Test Item"
        assert instance.email == "test@example.com"

    async def test_get_not_found(self, session: "AsyncSession") -> None:
        """Test if return type is None when trying to get a non-existent record."""

        repository: RepositoryTest = RepositoryTest(session=session)

        instance: RepositoryTestTable | None = await repository.get(id_=uuid4())

        assert instance is None

    async def test_update(self, session: "AsyncSession") -> None:
        """Test if a record can be updated with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)
        id_: UUID4 = uuid4()
        _: RepositoryTestTable = await repository.create(
            schema=CreateSchemaTest(
                id=id_,
                name="Test Item",
                email="test@example.com",
            ),
        )

        updated: RepositoryTestTable = await repository.update(
            id_=id_,
            schema=UpdateSchemaTest(
                name="Updated Item",
                email="updated@example.com",
            ),
        )

        assert updated.id == id_
        assert updated.name == "Updated Item"
        assert updated.email == "updated@example.com"

    async def test_update_not_found(self, session: "AsyncSession") -> None:
        """Test if an error is raised when trying to update a non-existent record."""

        repository: RepositoryTest = RepositoryTest(session=session)

        with pytest.raises(ObjectNotFoundError):
            _: RepositoryTestTable = await repository.update(id_=uuid4(), schema=UpdateSchemaTest(name="Updated Item"))

    async def test_delete(self, session: "AsyncSession") -> None:
        """Test if a record can be deleted with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)
        id_: UUID4 = uuid4()
        _: RepositoryTestTable = await repository.create(
            schema=CreateSchemaTest(
                id=id_,
                name="Test Item",
                email="test@example.com",
            ),
        )

        await repository.delete(id_=id_)

        instance: RepositoryTestTable | None = await repository.get(id_=id_)
        assert instance is None

    async def test_delete_not_found(self, session: "AsyncSession") -> None:
        """Test if an error is raised when trying to delete a non-existent record."""

        repository: RepositoryTest = RepositoryTest(session=session)

        with pytest.raises(ObjectNotFoundError):
            await repository.delete(id_=uuid4())

    async def test_bulk_create(self, session: "AsyncSession") -> None:
        """Test if multiple records can be created with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)
        create_data: list[CreateSchemaTest] = [
            CreateSchemaTest(name="Test Item 1"),
            CreateSchemaTest(name="Test Item 2"),
        ]

        _: list[RepositoryTestTable] = await repository.bulk_create(schema=create_data)

        assert len(await repository.all()) == 2  # noqa: PLR2004

    async def test_all(self, session: "AsyncSession") -> None:
        """Test if all records can be retrieved with the repository."""

        repository: RepositoryTest = RepositoryTest(session=session)
        create_data = [
            CreateSchemaTest(name="Test Item 1"),
            CreateSchemaTest(name="Test Item 2"),
        ]
        _: list[RepositoryTestTable] = await repository.bulk_create(schema=create_data)

        instances: list[RepositoryTestTable] = await repository.all()

        assert len(instances) == 2  # noqa: PLR2004
