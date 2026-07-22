import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

logger = logging.getLogger("app.core.security")


class SecurityManager:
    # Tunavuta siri moja kwa moja kutoka kwenye settings zilizothibitishwa
    SECRET_KEY = settings.JWT_SECRET.get_secret_value() if hasattr(settings.JWT_SECRET, "get_secret_value") else str(settings.JWT_SECRET)
    ALGORITHM = settings.ALGORITHM
    EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @classmethod
    def create_access_token(cls, user_id: Any, username: str) -> str:
        """
        Generates a secure, cryptographically signed JWT token string using PyJWT.
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=cls.EXPIRE_MINUTES)
        
        # RESILIENT CLAIMS: Tunahifadhi funguo zote mbili 'id' na 'user_id' kuzuia migongano
        payload = {
            "sub": str(username).lower().strip(),
            "id": str(user_id),
            "user_id": str(user_id),
            "username": str(username).lower().strip(),
            "exp": expire
        }
        
        logger.info(f"Issuing secure session token footprint for admin user: '{username}'")
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Cryptographically decodes and verifies an inbound PyJWT token string.
        """
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            username = payload.get("username") or payload.get("sub")
            user_id = payload.get("user_id") or payload.get("id")
            
            if username is None or user_id is None:
                logger.warning("Token tracking warning: Decoded payload claims are missing parameters.")
                return None
                
            logger.info(f"Token signature successfully verified for: '{username}'")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Cryptographic barrier: Session token has expired.")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Cryptographic barrier: Signature matching collapsed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected token analysis exception caught: {str(e)}")
            return None