import asyncio
import logging
import os
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

from app.core.config import settings
from app.utils.hashing import PasswordManager
from app.database.models.admin import Admin
# Ongeza import ya Base ili tuweze kutengeneza tables
from app.database.session import Base  # Hakikisha hii path ya Base ni sahihi kulingana na project yako

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app.seed_admin")

async def execute_administrative_seeding(db_session: AsyncSession = None) -> None:
    """
    Executes a hardened administrative database seeding operation.
    Safe for both standalone CLI invocation and server runtime cycles.
    """
    target_username = os.getenv("ADMIN_SEED_USERNAME")
    target_email = os.getenv("ADMIN_SEED_EMAIL", "hashimyg583@gmail.com")
    raw_secure_password = os.getenv("ADMIN_SEED_PASSWORD")

    if not target_username or not raw_secure_password:
        logger.warning("Seeding skipped: Access credentials unpopulated inside .env workspace profiles.")
        return

    local_engine = None
    if db_session is None:
        local_engine = create_async_engine(str(settings.DATABASE_URL))
        
        # 1. TENGENEZA TABLES ZOTE KWANZA KAMBA HAZIPO (AUTO-MIGRATION)
        async with local_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        local_factory = async_sessionmaker(bind=local_engine, class_=AsyncSession, expire_on_commit=False)
        session = local_factory()
    else:
        session = db_session

    try:
        query = select(Admin).where(Admin.username == target_username.lower().strip())
        result = await session.execute(query)
        existing_admin = result.scalars().first()

        if existing_admin:
            logger.info(f"Administrative account for user '{target_username.lower()}' already exists. Skipping.")
            return

        hashed_password = PasswordManager.hash_password(raw_secure_password)

        root_admin = Admin(
            username=target_username.lower().strip(),
            email=target_email.lower().strip(),
            hashed_password=hashed_password,
            is_active=True
        )

        session.add(root_admin)
        await session.commit()
        
        logger.info(f"SUCCESS: Root administrative profile deployed into PostgreSQL engine cleanly. Username: '{target_username.lower().strip()}'")

    except Exception as e:
        await session.rollback()
        logger.critical(f"Critical seeding error caught: {str(e)}")
    finally:
        if db_session is None:
            await session.close()
            await local_engine.dispose()


if __name__ == "__main__":
    asyncio.run(execute_administrative_seeding())