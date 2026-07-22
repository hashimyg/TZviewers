import time
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func, and_
import redis.asyncio as aioredis

from app.dependencies.database import get_db
from app.core.config import settings
from app.database.models.contact import Contact

logger = logging.getLogger("app.api.health")
router = APIRouter(prefix="/health", tags=["System Monitoring"])

@router.get("", status_code=status.HTTP_200_OK)
async def check_system_infrastructure_health(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    start_time = time.time()
    postgres_healthy, redis_healthy = False, False
    postgres_latency, redis_latency = 0.0, 0.0

    # 1. POSTGRESQL CHECK & LIVE COUNT MATRIX
    live_approved_count = 0
    try:
        pg_start = time.time()
        await db.execute(text("SELECT 1"))
        postgres_latency = (time.time() - pg_start) * 1000
        postgres_healthy = True

        # LIVE ENGINE COUNT: Inasoma namba halisi ya approved contacts sekunde hii
        count_stmt = select(func.count(Contact.id)).where(
            and_(Contact.is_approved == True, Contact.deleted_at == None)
        )
        count_res = await db.execute(count_stmt)
        live_approved_count = count_res.scalar() or 0
    except Exception as pg_err:
        logger.error(f"PostgreSQL health check failed: {str(pg_err)}")
        postgres_healthy = False

    # 2. REDIS CACHE CHECK
    try:
        redis_start = time.time()
        cache_client = aioredis.from_url(str(settings.REDIS_URL))
        await cache_client.ping()
        redis_latency = (time.time() - redis_start) * 1000
        redis_healthy = True
        await cache_client.close()
    except Exception as redis_err:
        logger.error(f"Redis health check failed: {str(redis_err)}")
        redis_healthy = False

    total_execution_runtime_ms = (time.time() - start_time) * 1000

    health_metrics = {
        "status": "UP" if (postgres_healthy and redis_healthy) else "DOWN",
        "environment": settings.ENVIRONMENT,
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "total_check_latency_ms": round(total_execution_runtime_ms, 2),
        "live_counter": live_approved_count, # 🎯 INJECTED: Thamani halisi ya namba za database
        "services": {
            "postgres": {"status": "HEALTHY" if postgres_healthy else "UNHEALTHY", "latency_ms": round(postgres_latency, 2)},
            "redis": {"status": "HEALTHY" if redis_healthy else "UNHEALTHY", "latency_ms": round(redis_latency, 2)}
        }
    }

    if not postgres_healthy or not redis_healthy:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_metrics)

    return health_metrics
