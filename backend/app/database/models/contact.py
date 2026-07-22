import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

class Contact(Base):
    """
    SQLAlchemy Model representing public shared contacts.
    Symmetrically bound to align fields for smooth client injection.
    """
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True
    )
    
    phone_number: Mapped[str] = mapped_column(
        String(16), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    is_approved: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    upload_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    upload = relationship(
        "Upload", 
        back_populates="contacts"
    )
    
    consent_given: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    
    consent_given_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )
    
    terms_version: Mapped[str] = mapped_column(
        String(10),
        default="v1.0",
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

Index("idx_contacts_search", Contact.first_name, Contact.last_name, Contact.phone_number)