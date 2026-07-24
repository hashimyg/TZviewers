import logging
import bcrypt

logger = logging.getLogger("app.security")


class PasswordManager:
    """
    Hardened Cryptographic Ingestion Engine.
    Executes raw high-entropy salted Bcrypt one-way hashing and secure 
    constant-time verification to prevent timing side-channel attacks.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Computes a secure, highly random salted Bcrypt hash at a strict 
        round 12 computational cost factor.
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Validates raw input strings against stored persistent database hashes.
        Uses C-level constant-time evaluation to completely block timing exploit vectors.
        """
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Cryptographic verification sub-loop failure: {str(e)}")
            return False

    @staticmethod
    def check_and_rehash_needed(hashed_password: str) -> bool:
        """
        Safe prefix checking that accepts both valid standard Bcrypt prefixes ($2a$ and $2b$).
        """
        try:
            # Accepts standard Bcrypt variants cleanly without triggering unnecessary DB writes
            return not (hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"))
        except Exception:
            return False