import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Upload(Base):
    """
    SQLAlchemy Model representing bulk data ingestion batches (CSV/VCF uploads).
    Provides strict structural logging and tracking for audit and analysis layers.
    """
    __tablename__ = "uploads"

    # 1. HARDENED IDENTIFIER LAYER (PostgreSQL Native UUID v4)
    # Mitigates scraping and ensures maximum index clustering efficiency
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4, 
        index=True
    )
    
    # 2. FILE TRACKING LAYER (Security Defended)
    # Stores clean, sanitized system-generated filenames to completely prevent path traversal attacks
    filename: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Stores the raw original user-provided filename strictly for logging purposes
    original_filename: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # TRACKING ENGINE METRICS (Data Integrity Layers)
    file_size: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )
    
    total_records_found: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False
    )
    
    # Ingestion tracking categories: e.g., 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
    status: Mapped[str] = mapped_column(
        String(20), 
        default="PENDING", 
        nullable=False, 
        index=True
    )
    
    # 3. ORM RELATIONSHIP LINK (Bi-Directional Mapping Resolved)
    # Smoothly maps back to the contacts child rows for easy multi-batch management
    contacts = relationship(
        "Contact", 
        back_populates="upload", 
        cascade="all, delete-orphan"
    )
    
    # 4. DATABASE-SIDE AUDIT TIMESTAMPS
    # Strictly isolated at the engine block level to prevent system time tampering
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
