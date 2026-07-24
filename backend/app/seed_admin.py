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
from app.database.session import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app.seed_admin")

async def execute_administrative_seeding(db_session: AsyncSession = None) -> None:
    """
    Executes a hardened administrative database seeding operation.
    Safe for both standalone CLI invocation and server runtime cycles.
    Dynamically synchronizes password updates for existing administrative profiles.
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
        normalized_username = target_username.lower().strip()
        normalized_email = target_email.lower().strip()

        query = select(Admin).where(Admin.username == normalized_username)
        result = await session.execute(query)
        existing_admin = result.scalars().first()

        # Hash credentials using raw Bcrypt
        hashed_password = PasswordManager.hash_password(raw_secure_password)

        if existing_admin:
            # UPDATE EXISTING PROFILE WITH NEW PASSWORD FROM ENV
            existing_admin.hashed_password = hashed_password
            existing_admin.email = normalized_email
            existing_admin.is_active = True
            
            await session.commit()
            logger.info(f"SUCCESS: Administrative account '{normalized_username}' password & details updated cleanly.")
            return

        # CREATE NEW PROFILE IF USER DOES NOT EXIST
        root_admin = Admin(
            username=normalized_username,
            email=normalized_email,
            hashed_password=hashed_password,
            is_active=True
        )

        session.add(root_admin)
        await session.commit()
        
        logger.info(f"SUCCESS: Root administrative profile deployed into PostgreSQL engine cleanly. Username: '{normalized_username}'")

    except Exception as e:
        await session.rollback()
        logger.critical(f"Critical seeding error caught: {str(e)}")
    finally:
        if db_session is None:
            await session.close()
            await local_engine.dispose()


if __name__ == "__main__":
    asyncio.run(execute_administrative_seeding())