import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.database import get_db
from app.database.models.admin import Admin
from app.core.security import SecurityManager
from app.exceptions.base import AuthenticationError

logger = logging.getLogger("app.dependencies.auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """
    Guarded Security Layer.
    Uses SecurityManager to decode tokens symmetrically and fetch the active Admin database record.
    """
    logger.info("Security tracking layer intercepting active token footprint parameters...")
    
    try:
        payload = SecurityManager.decode_access_token(token)
        if payload is None:
            logger.warning("Cryptographic signature failure: Decoded payload returned None block profiles.")
            raise AuthenticationError()
            
        username: str = payload.get("username") or payload.get("sub")
        user_id: str = payload.get("user_id") or payload.get("id")
        
        if username is None or user_id is None:
            logger.warning("Identity verification failure: Claims profiles are missing variables.")
            raise AuthenticationError()
            
    except Exception as e:
        logger.error(f"Cryptographic session decoding collapsed: {str(e)}")
        raise AuthenticationError()

    query = select(Admin).where(Admin.username == username.lower().strip())
    result = await db.execute(query)
    admin = result.scalars().first()

    if admin is None or not admin.is_active:
        logger.warning(f"Access Denied: Administrative profile matching token keys '{username}' is offline.")
        raise AuthenticationError()

    logger.info(f"Identity authorized successfully for active session control: '{admin.username}'.")
    return admin