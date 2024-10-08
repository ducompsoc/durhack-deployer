import asyncio
from logging.config import fileConfig
from os import environ as os_environ
from urllib.parse import urlparse, urlunparse, ParseResult as UrlParseResult

from dotenv import dotenv_values

from sqlalchemy import pool, exc, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# This contains variables from `<repo>/production-deployer/.env` and/or `os.getenv()`
environment = {
    **os_environ,
    **dotenv_values(),
}

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = environment["DATABASE_URL"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def create_database_if_not_exists() -> None:
    db_url = environment["DATABASE_URL"]
    parsed_db_url = urlparse(db_url)
    database_name = parsed_db_url.path
    if database_name.startswith("/"):
        database_name = database_name[1:]
    if "/" in database_name:
        raise ValueError(f'Database name {database_name} is invalid')
    
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            print(f'Database {database_name} already exists.')
            return
    except exc.OperationalError:
        pass

    print(f'Database {database_name} does not exist. Creating now.')
    metadb_url = UrlParseResult(
        scheme=parsed_db_url.scheme,
        netloc=parsed_db_url.netloc,
        path="/postgres",
        params="",
        query="",
        fragment="",
    ).geturl()
    engine = create_async_engine(metadb_url)
    
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f'create database "{database_name}"'))
    print(f'Created database {database_name}.')

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    
    await create_database_if_not_exists()

    connectable = async_engine_from_config(
        { 'sqlalchemy.url': environment["DATABASE_URL"] },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
