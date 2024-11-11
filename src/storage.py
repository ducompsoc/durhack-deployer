from os import environ as os_environ
from dotenv import dotenv_values

from sqlalchemy import String, exists
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from data_types import GitHubEvent

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


engine = create_async_engine(environment["DATABASE_URL"], echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def persist_handled_event(event: GitHubEvent) -> None:
    async with async_session() as session:
        if await session.scalar(
            exists()
            .where(PersistedEvent.id == event.id)
            .select()
        ):
            return
        persisted_event = PersistedEvent(id=event.id)
        session.add(persisted_event)
        await session.commit()


async def persisted_event_exists(event: GitHubEvent) -> bool:
    async with async_session() as session:
        return await session.scalar(
            exists()
            .where(PersistedEvent.id == event.id)
            .select()
        )
