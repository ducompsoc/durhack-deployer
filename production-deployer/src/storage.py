from os import environ as os_environ
from dotenv import dotenv_values

from sqlalchemy import String, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

environment = {
    **os_environ,
    **dotenv_values(),
}


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "event"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    def __repr__(self) -> str:
        return f"Event(id={self.id!r})"


engine = create_async_engine(environment["DATABASE_URL"], echo=True)
