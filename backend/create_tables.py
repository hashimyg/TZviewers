import asyncio
import logging
import sys
from pathlib import Path

# Imarisha mazingira ya package routing paths
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.session import engine, Base
from app.database.models.admin import Admin
from app.database.models.contact import Contact

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app.create_tables")

async def forge_database_schema_layers():
    logger.info("Initializing database schema validation structures inside isolated PostgreSQL...")
    # FIXED: Muundo rasmi wa kiwanda wa SQLAlchemy 2.0+ AsyncIO Context Manager
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("SUCCESS: Database schema layers forged completely inside PostgreSQL cluster.")
        except Exception as e:
            logger.critical(f"CRITICAL MATRIX FAILURE: Schema generation collapsed: {str(e)}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(forge_database_schema_layers())