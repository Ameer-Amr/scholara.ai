import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from backend.core.database import Base
from alembic import context
from backend.core.config import settings
from backend.models.db_models import User, OAuthAccount

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

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
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # 1. Fetch your clean async connection string directly from your Pydantic settings
    db_url = settings.DATABASE_URL

    # 2. Build the genuine async engine directly
    connectable = create_async_engine(db_url, poolclass=pool.NullPool)

    # 3. Define the async task that Alembic handles behind the scenes
    async def run_async_migrations():
        async with connectable.connect() as connection:
            # Safely passes the sync context configuration over the async loop
            await connection.run_sync(do_run_migrations)

    # 4. Helper function to actually commit the migration steps
    def do_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    # 5. Bootstrap the async workflow inside the synchronous entry point
    try:
        asyncio.run(run_async_migrations())
    except Exception as e:
        print(f"Migration execution failed: {e}")
        raise e


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
