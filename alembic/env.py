import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
from app.models.user import *  # Ensure this imports all necessary models
from app.db import postgres_url
from app.utilities.logger import logger

import os
from dotenv import load_dotenv

load_dotenv()
development = True if os.getenv("ENVIRONMENT") == 'development' else False

target_metadata = Base.metadata


def run_migrations(connection):
    context.configure(
        connection=connection,
        compare_type=True,
        dialect_opts={'paramstyle': 'named'},
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema=target_metadata.schema,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(postgres_url)

    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)

    await connectable.dispose()


def main():
    try:
        asyncio.run(run_migrations_online())
    except Exception:
        logger.error("Error running migrations", exc_info=True)


if not development:
    main()
