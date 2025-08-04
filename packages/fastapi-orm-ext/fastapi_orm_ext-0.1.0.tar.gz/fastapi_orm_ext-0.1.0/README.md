# FastApi ORM Extensions

[![PyPI - Version](https://img.shields.io/pypi/v/fastapi-orm-ext.svg)](https://pypi.org/project/fastapi-orm-ext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-orm-ext.svg)](https://pypi.org/project/fastapi-orm-ext)

-----

## Table of Contents
- [Installation](#installation)
- [About](#About)
- [License](#license)
- [Contribution](#contribution)


## Installation
```bash
pip install fastapi-orm-ext
```
or
```bash
uv add fastapi-orm-ext
```
or
```bash
poetry add fastapi-orm-ext
```
etc


## About
This library provides preset base class for your tables and repositories.
#### Use TableBase like so:
```python
from fastapi_orm_ext.table import TableBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Table(TableBase, DeclarativeBase):
    # you can use this class in alembic's env.py file
    # to specify target_metadata for example
    __abstract__: bool = True


class User(Table):
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str | None] = mapped_column(nullable=True)
```

TableBase consists of four mixins:
- NameConventionMixin: handles name convention;
- TableNameMixin: takes model's class name and convert it to snake case, use this name while creating table in DB;
- TimestampsMixin: handles when record was created and updated;
- UUIDPrimaryKeyMixin: makes PK of UUID4 type.

If you don't need one or more of following mixins, create your own TableBase.

#### Use Repository like so:
```python
from fastapi_orm_ext.repository import RepositoryBase
from pydantic import BaseModel

from app.tables import User
# the variant to get async session
from app.utils import async_session


class CreateUserSchema(BaseModel):
    name: str
    email: str | None


class UserRepository(RepositoryBase[User]):
    # specify the model to interact with
    model = User
    # choose flush or commit
    auto_flush = True
    auto_commit = False

    # there you can define your methods
    def get_by_email(self, email: str) -> User | None:
        return (
            await self.session.execute(
                statement=select(self.model).where(self.model.email == email),
            )
        ).scalar()

# initialize UserRepository
repo = UserRepository(async_session)
# create new record in users table
data = CreateUserSchema(name="Bob", email="bob@gmail.com")
await repo.create(data)

# get record in users table by Bob's email
res: list[User] = await repo.get_by_email("bob@gmail.com")
print(res)
```

To see what else RepositoryBase can do, visit the source code of interface RepositoryBase inheriting from


## License
`fastapi-orm-ext` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


## Contribution
Install repository:
```bash
https://github.com/pkozhem/fastapi-orm-ext.git
```

Create virtual environment, activate it and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv sync
```

Create new branch from actual tag:
```bash
git checkout <tag>
git branch pull-<fix, feat, impr>: Short branch desc
```

Pull your changes and create pull request:
```bash
git pull origin <your_branch_name>
```
