import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import async_session_factory

logger = logging.getLogger("app.dependencies.database")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Scops down an independent, context-bound Asynchronous SQLAlchemy database session.
    Automatically commits or rolls back atomic transactions, ensuring connections
    are cleanly closed and returned to the connection pool without leakage.
    """
    async with async_session_factory() as session:
        try:
            # Yields the thread-safe connection mapping block directly to routers
            yield session
        except Exception as e:
            logger.error(
                f"Database session execution exception caught down the route tree: {str(e)}"
            )
            await session.rollback()
            raise
        finally:
            # Enforces immediate execution closure to prevent memory/socket drift
            await session.close()
