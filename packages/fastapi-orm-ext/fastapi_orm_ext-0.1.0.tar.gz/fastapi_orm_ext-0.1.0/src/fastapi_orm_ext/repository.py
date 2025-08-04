from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, override

from pydantic import BaseModel
from sqlalchemy import select

from fastapi_orm_ext.errors import ObjectNotFoundError, RepositoryConsistentError
from fastapi_orm_ext.table import TableBase

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from pydantic import UUID4
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.selectable import ForUpdateParameter

__all__ = ("RepositoryBase",)

UpdateSchema = BaseModel
CreateSchema = BaseModel


class IBaseRepository[ConcreteTable: TableBase](ABC):
    """Interface for any repositories."""

    @abstractmethod
    async def refresh(
        self,
        instance: ConcreteTable,
        attribute_names: "Iterable[str] | None" = None,
        with_for_update: "ForUpdateParameter" = None,
    ) -> None:
        """Refresh instance from database."""

    @abstractmethod
    async def get(self, id_: "str | UUID4") -> ConcreteTable | None:
        """Get instance by ID."""

    @abstractmethod
    async def all(self) -> list[ConcreteTable]:
        """Get all instances from table."""

    @abstractmethod
    async def create(self, schema: CreateSchema) -> ConcreteTable:
        """Create new instance in table."""

    @abstractmethod
    async def bulk_create(self, schema: "Sequence[CreateSchema]") -> list[ConcreteTable]:
        """Create new instances in table."""

    @abstractmethod
    async def update(self, id_: "str | UUID4", schema: UpdateSchema) -> ConcreteTable:
        """Update instance in table by ID."""

    @abstractmethod
    async def delete(self, id_: "str | UUID4") -> None:
        """Delete instance from table by ID."""


class BaseRepositoryBase[ConcreteTable: TableBase](IBaseRepository[ConcreteTable], ABC):
    """Base class for SQLAlchemy repository."""

    model: type[ConcreteTable]
    auto_commit: bool
    auto_flush: bool

    def _check_consistent(self) -> None:
        """Check if repository is consistent."""

        msg: str = ""
        if self.auto_commit is False and self.auto_flush is False:
            msg = "You should specify 'auto_commit' or 'auto_flush parameter."
            raise RepositoryConsistentError(msg)
        if self.auto_commit is True and self.auto_flush is True:
            msg = "You should set in 'True' only one parameter: 'auto_commit' or 'auto_flush', not both of them."
            raise RepositoryConsistentError(msg)
        if not self.model:
            msg = "You should specify 'model' parameter."
            raise RepositoryConsistentError(msg)


class RepositoryBase[ConcreteTable: TableBase](BaseRepositoryBase[ConcreteTable], ABC):
    """Base class for all SQLAlchemy repositories."""

    model: type[ConcreteTable]
    auto_commit: bool = False
    auto_flush: bool = True

    def __init__(self, session: "AsyncSession") -> None:
        self.session: AsyncSession = session
        self._check_consistent()

    @staticmethod
    def _get_create_data(schema: CreateSchema) -> dict[str, Any]:
        """Return dict data a for creating new instance."""

        return schema.model_dump()

    @staticmethod
    def _get_update_data(schema: UpdateSchema) -> dict[str, Any]:
        """Return dict data a for updating new instance."""

        return schema.model_dump(exclude_unset=True)

    async def commit(self) -> None:
        if self.auto_commit:
            await self.session.commit()
        else:
            await self.session.flush()

    @override
    async def refresh(
        self,
        instance: ConcreteTable,
        attribute_names: "Iterable[str] | None" = None,
        with_for_update: "ForUpdateParameter" = None,
    ) -> None:
        if self.auto_commit:
            await self.session.refresh(
                instance=instance,
                attribute_names=attribute_names,
                with_for_update=with_for_update,
            )

    @override
    async def get(self, id_: "str | UUID4") -> ConcreteTable | None:
        return (
            await self.session.execute(
                statement=select(self.model).where(self.model.id == id_),
            )
        ).scalar()

    @override
    async def all(self) -> list[ConcreteTable]:
        res: Sequence[ConcreteTable] = (
            (
                await self.session.execute(
                    statement=select(self.model),
                )
            )
            .scalars()
            .all()
        )
        return list(res) if res else []

    @override
    async def create(self, schema: CreateSchema) -> ConcreteTable:
        data: dict[str, Any] = self._get_create_data(schema=schema)
        instance: ConcreteTable = self.model(**data)
        self.session.add(instance=instance)
        await self.commit()
        await self.refresh(instance=instance)
        return instance

    @override
    async def bulk_create(self, schema: "Sequence[CreateSchema]") -> list[ConcreteTable]:
        instances: list[ConcreteTable] = [self.model(**self._get_create_data(schema=model)) for model in schema]
        self.session.add_all(instances=instances)

        await self.commit()

        for instance in instances:
            await self.refresh(instance=instance)

        return instances

    @override
    async def update(self, id_: "str | UUID4", schema: UpdateSchema) -> ConcreteTable:
        instance: ConcreteTable | None = await self.get(id_=id_)
        if not instance:
            raise ObjectNotFoundError(id_=id_) from None

        data: dict[str, Any] = self._get_update_data(schema=schema)
        for k, v in data.items():
            setattr(instance, k, v)

        await self.commit()
        await self.refresh(instance=instance)

        return instance

    @override
    async def delete(self, id_: "str | UUID4") -> None:
        instance: ConcreteTable | None = await self.get(id_=id_)
        if instance is None:
            raise ObjectNotFoundError(id_=id_) from None

        await self.session.delete(instance=instance)
        await self.commit()
