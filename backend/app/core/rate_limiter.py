from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Enforce globally tracked rate limits tied to client IP addresses over Redis storage blocks
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=str(settings.REDIS_URL),
    enabled=(settings.ENVIRONMENT != "testing")
)
