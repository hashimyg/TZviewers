import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 🛡️ SYSTEM ENVIRONMENT CONFIGURATION:
# Tunavuta kamba kamili ya siri ya database URL kutoka kwenye mfumo wa mazingira (.env)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback salama inayosoma siri za mazingira ya ndani ya Docker subnet
    DATABASE_URL = "postgresql+asyncpg://vcf_admin:VCFGlowMaster2026Secure!@vcf_postgres/vcf_platform_db"

# Engine pool salama ya ki-PostgreSQL kwa SQLAlchemy 2.0+
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=25
)

# Kiwanda cha kutengenezea session pools salama (SQLAlchemy 2.0 Standard)
async_session_factory = async_sessionmaker(
    bind=engine, 
    autocommit=False,
    autoflush=False,
    expire_on_commit=False, 
    class_=AsyncSession
)

# FIXED: Tunatumia DeclarativeBase kama Class rasmi ya SQLAlchemy 2.0+
# Hii inazuia kabisa migongano yote ya ma-import na kuwasha seva ya FastAPI hewani!
class Base(DeclarativeBase):
    pass
