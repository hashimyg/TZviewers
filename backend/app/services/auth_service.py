import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.admin import Admin
from app.schemas.auth import AdminLogin, Token
from app.utils.hashing import PasswordManager
from app.core.security import SecurityManager
from app.exceptions.base import AuthenticationError, AccountDisabledError

logger = logging.getLogger("app.auth_service")


class AuthService:
    """
    Core administrative authentication execution engine.
    Orchestrates identity verification, state compliance checks, and session provisioning.
    Symmetrically bound to the Direct Native Bcrypt infrastructure.
    """

    @staticmethod
    async def authenticate_admin(login_data: AdminLogin, db: AsyncSession) -> Token:
        """
        Executes a high-security administrative credential verification transaction.
        Enforces defensive timing mitigation and runtime hash factor optimization.
        """
        # STEP A: Query user via parameterized filters (username is pre-normalized to lowercase via schema)
        query = select(Admin).where(Admin.username == login_data.username.lower().strip())
        result = await db.execute(query)
        admin = result.scalars().first()

        # DEFENSIVE MITIGATION: Prevent Username Enumeration via Timing Side-Channel Attacks
        if admin is None:
            # Fake hash structure forces PasswordManager to burn standard computational cycles
            PasswordManager.verify_password(
                login_data.password, 
                "$2b$12$L7R38mU7Jj1VdB7b4K0eYu7UjGvB6f7E6G6h6i6j6k6l6m6n6o6p6"
            )
            logger.warning(f"Unsuccessful authentication attempt: Username '{login_data.username}' not found.")
            raise AuthenticationError()

        # STEP B: Validate administrative account state compliance
        if not admin.is_active:
            logger.warning(f"Security Alert: Disabled administrative login attempt blocked for account '{admin.username}'.")
            raise AccountDisabledError()

        # STEP C: Perform cryptographic password comparison
        is_password_valid = PasswordManager.verify_password(login_data.password, admin.hashed_password)
        if not is_password_valid:
            logger.warning(f"Unsuccessful authentication attempt: Invalid password provided for account '{admin.username}'.")
            raise AuthenticationError()

        # STEP D: DIRECT CRYPTOGRAPHIC PATTERN ALIGNMENT INSPECTION
        # Safely checks if the hash structure requires optimization back into PostgreSQL layers
        if PasswordManager.check_and_rehash_needed(admin.hashed_password):
            logger.info(f"Upgrading cryptographic hash parameters dynamically for active account: '{admin.username}'.")
            admin.hashed_password = PasswordManager.hash_password(login_data.password)
            db.add(admin)
            await db.commit()

        # STEP E: Provision Signed Session Cryptographic Token using native SecurityManager
        access_token = SecurityManager.create_access_token(user_id=admin.id, username=admin.username)
        
        logger.info(f"Administrative session successfully provisioned for tracking context: '{admin.username}'.")
        
        return Token(access_token=access_token)
