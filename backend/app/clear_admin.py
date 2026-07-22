import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import delete

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

from app.core.config import settings
from app.database.session import async_session_factory, engine
from app.database.models.admin import Admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app.clear_admin")

async def purge_old_admin_record() -> None:
    logger.info("Connecting to database using active environment configurations...")
    async with async_session_factory() as session:
        try:
            # Force delete any existing administrative users named 'admin'
            statement = delete(Admin).where(Admin.username == "admin")
            result = await session.execute(statement)
            await session.commit()
            logger.info("SUCCESS: Old administrative database rows purged completely.")
        except Exception as e:
            await session.rollback()
            logger.critical(f"Database operation failed: {str(e)}")
        finally:
            await session.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(purge_old_admin_record())
