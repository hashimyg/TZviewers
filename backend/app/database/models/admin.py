import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Admin(Base):
    """
    SQLAlchemy Model for the system administrator.
    Protects login credentials and maintains system administrative state.
    """
    __tablename__ = "admins"

    # SECURITY GUARD: UUID v4 prevents ID enumeration attacks
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    
    # SECURITY GUARD: Enforced strict lengths, case-insensitive logic handled at schema
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    # SECURITY GUARD: This column stores ONLY salted Bcrypt hashes (Never plain-text)
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
    )
    
    # AUDIT LAYER: Timezone-aware timestamps tracking user records
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
