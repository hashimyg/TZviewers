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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app.seed_admin")

engine = create_async_engine(str(settings.DATABASE_URL))
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def execute_administrative_seeding() -> None:
    """
    Executes a hardened administrative database seeding operation.
    Extracts access metrics cleanly from environment memory blocks.
    """
    target_username = os.getenv("ADMIN_SEED_USERNAME")
    # FIXED: Email yako ya ukweli sasa hivi imejifunga kiwanda bila kuvunja kodi
    target_email = os.getenv("ADMIN_SEED_EMAIL", "hashimyg583@gmail.com")
    raw_secure_password = os.getenv("ADMIN_SEED_PASSWORD")

    if not target_username or not raw_secure_password:
        logger.critical("Transaction aborted: Access credentials unpopulated inside host .env workspace profiles.")
        return

    logger.info("Connecting to PostgreSQL container inside isolated Docker layer...")

    async with session_factory() as session:
        try:
            query = select(Admin).where(Admin.username == target_username.lower().strip())
            result = await session.execute(query)
            existing_admin = result.scalars().first()

            if existing_admin:
                logger.warning(f"Administrative account for user '{target_username.lower()}' already exists. Skipping.")
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
            
            logger.info(
                f"SUCCESS: Root administrative profile deployed into PostgreSQL engine cleanly. "
                f"Username Token: '{target_username.lower().strip()}' | Clearance Level: MASTER_ADMIN"
            )

        except Exception as e:
            await session.rollback()
            logger.critical(f"Critical seeding error caught during transaction processing: {str(e)}")
        finally:
            await session.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(execute_administrative_seeding())
