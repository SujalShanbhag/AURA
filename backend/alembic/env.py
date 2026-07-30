from __future__ import annotations

import asyncio

from logging.config import fileConfig

from sqlalchemy import pool

from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context


from app.core.config import settings

from app.core.database import Base


# Import all models so Alembic detects them

from app.models.user import User
from app.models.session import Session
from app.models.refresh_token import RefreshToken
from app.models.memory import Memory



config = context.config


fileConfig(
    config.config_file_name
)



target_metadata = Base.metadata



def run_migrations_offline():

    url = settings.DATABASE_URL

    context.configure(

        url=url,

        target_metadata=target_metadata,

        literal_binds=True,

        dialect_opts={
            "paramstyle": "named"
        },

    )


    with context.begin_transaction():

        context.run_migrations()



def do_run_migrations(connection):

    context.configure(

        connection=connection,

        target_metadata=target_metadata,

    )


    with context.begin_transaction():

        context.run_migrations()



async def run_migrations_online():

    connectable = async_engine_from_config(

        {
            "sqlalchemy.url":
                settings.DATABASE_URL
        },

        prefix="sqlalchemy.",

        poolclass=pool.NullPool,

    )


    async with connectable.connect() as connection:

        await connection.run_sync(
            do_run_migrations
        )


    await connectable.dispose()



if context.is_offline_mode():

    run_migrations_offline()

else:

    asyncio.run(
        run_migrations_online()
    )