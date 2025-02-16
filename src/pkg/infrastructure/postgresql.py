import contextlib
from typing import AsyncIterator

from alembic import context
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncSession,
)
from sqlalchemy.ext.declarative import declarative_base

ALEMBIC_CONFIG_PATH = "alembic.ini"

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self, uri: str, engine_kwargs=None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(uri, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)
        self._uri = uri

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def run_migrations(self):
        """Run Alembic migrations programmatically in online mode."""
        config = Config(ALEMBIC_CONFIG_PATH)
        config.set_main_option("sqlalchemy.url", self._uri)

        async with self._engine.begin() as connection:
            await connection.run_sync(
                lambda conn: context.configure(
                    connection=conn, target_metadata=Base.metadata, compare_type=True
                )
            )
            await connection.run_sync(context.run_migrations)

        await self._engine.dispose()
