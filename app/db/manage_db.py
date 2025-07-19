"""
Async database session management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from app.db.models import Rental
from sqlmodel import SQLModel
from app.core.config import settings
from sqlalchemy.exc import SQLAlchemyError


def get_async_engine() -> AsyncEngine:
    """Return async database engine."""
    try:
        async_engine: AsyncEngine = create_async_engine(
            settings.DATABASE_URL_SUPABASE,
            echo=settings.LOG_LEVEL == "DEBUG",
            future=True,
        )
    except SQLAlchemyError as e:
        raise RuntimeError(f"Failed to create async engine: {e}")
    return async_engine


engine = get_async_engine()


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session.

    All conversations with the database are established via the session
    objects. Also. the sessions act as holding zone for ORM-mapped objects.
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
