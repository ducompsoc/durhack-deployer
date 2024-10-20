from os import environ as os_environ
from dotenv import dotenv_values

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

environment = {
    **os_environ,
    **dotenv_values(),
}


class Base(DeclarativeBase):
    pass


class PersistedEvent(Base):
    __tablename__ = "event"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    def __repr__(self) -> str:
        return f"Event(id={self.id!r})"


engine = create_async_engine(environment["DATABASE_URL"], echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
