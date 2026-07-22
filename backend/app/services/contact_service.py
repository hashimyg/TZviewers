import uuid
import logging
from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database.models.contact import Contact
from app.schemas.contact import ContactCreate
from app.exceptions.base import DuplicateContactError, EntityNotFoundError

logger = logging.getLogger("app.contact_service")


class ContactService:
    """
    Core business logic utility managing the database lifecycle, administrative 
    approval processing states, and soft deletion routines for phone numbers.
    """

    @staticmethod
    async def create_public_contact(contact_in: ContactCreate, db: AsyncSession, upload_id: uuid.UUID | None = None) -> Contact:
        """
        Processes a safe public entry insertion. Enforces absolute database-level 
        uniqueness checks before finalizing records.
        """
        # STEP A: Race-Condition Defense Check
        # Query if the normalized phone string already exists in the system (active or soft-deleted)
        query = select(Contact).where(Contact.phone_number == contact_in.phone_number)
        result = await db.execute(query)
        existing_contact = result.scalars().first()

        if existing_contact:
            # If it was soft-deleted previously, we restore it and renew consent parameters safely
            if existing_contact.deleted_at is not None:
                logger.info(f"Restoring previously soft-deleted contact record: {contact_in.phone_number}")
                existing_contact.deleted_at = None
                existing_contact.is_approved = False  # Reset state to pending admin verification
                existing_contact.first_name = contact_in.sanitize_names(contact_in.first_name)
                existing_contact.last_name = contact_in.sanitize_names(contact_in.last_name)
                existing_contact.consent_given = contact_in.consent_given
                existing_contact.consent_given_at = func.now()
                await db.commit()
                return existing_contact
                
            logger.warning(f"Rejected duplicate phone ingestion attempt: {contact_in.phone_number}")
            raise DuplicateContactError()

        # STEP B: Construct clean model entity
        new_contact = Contact(
            first_name=contact_in.first_name,
            last_name=contact_in.last_name,
            phone_number=contact_in.phone_number,
            consent_given=contact_in.consent_given,
            upload_id=upload_id,
            is_approved=False  # Must be explicitly audited and unlocked by the Administrator
        )

        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        
        logger.info(f"Successfully staged contact entry under pending verification queue: {new_contact.id}")
        return new_contact

    @staticmethod
    async def get_approved_contacts_for_download(db: AsyncSession) -> List[Contact]:
        """
        Fetches the complete active dataset of clean, approved numbers for VCF compile streaming.
        Bypasses pagination limits intentionally to generate the Master corporate directory.
        """
        query = select(Contact).where(
            and_(
                Contact.is_approved == True,
                Contact.deleted_at == None
            )
        ).order_by(Contact.first_name.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_paginated_contacts_admin(
        db: AsyncSession, 
        page: int = 1, 
        limit: int = 50, 
        search_query: str | None = None,
        pending_only: bool = False
    ) -> Tuple[List[Contact], int]:
        """
        Advanced administrative index query. Leverages high-performance composite index paths 
        to execute lightning-fast paginated filters over tens of thousands of active numbers.
        """
        # Enforce safe mathematical baseline boundaries
        if page < 1: page = 1
        if limit < 1 or limit > 100: limit = 50
        offset = (page - 1) * limit

        # Build dynamic query constraints
        conditions = [Contact.deleted_at == None]
        
        if pending_only:
            conditions.append(Contact.is_approved == False)

        if search_query:
            clean_search = f"%{search_query.strip()}%"
            # Multi-field condition mapping matches our B-Tree composite index sequence
            conditions.append(
                func.or_(
                    Contact.first_name.ilike(clean_search),
                    Contact.last_name.ilike(clean_search),
                    Contact.phone_number.ilike(clean_search)
                )
            )

        # Build execution statements
        base_stmt = select(Contact).where(and_(*conditions))
        
        # Pull transactional sub-count metrics cleanly
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_count_res = await db.execute(count_stmt)
        total_count = total_count_res.scalar() or 0

        # Apply spatial offset windows to slice response feeds safely
        query_stmt = base_stmt.order_by(Contact.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query_stmt)
        contacts = list(result.scalars().all())

        return contacts, total_count

    @staticmethod
    async def approve_contact_entry(contact_id: uuid.UUID, db: AsyncSession) -> Contact:
        """
        Updates verification permission status, permitting inclusion into the public master distribution pool.
        """
        query = select(Contact).where(and_(Contact.id == contact_id, Contact.deleted_at == None))
        result = await db.execute(query)
        contact = result.scalars().first()

        if not contact:
            raise EntityNotFoundError("Target contact record was not found or has been removed.")

        contact.is_approved = True
        await db.commit()
        logger.info(f"Administrative validation cleared for contact entity tracking signature: {contact_id}")
        return contact

    @staticmethod
    async def soft_delete_contact_entry(contact_id: uuid.UUID, db: AsyncSession) -> None:
        """
        Executes a safe historical soft-delete operation. Flags records out of circulation 
        without corrupting historical relational references inside the upload logs.
        """
        query = select(Contact).where(and_(Contact.id == contact_id, Contact.deleted_at == None))
        result = await db.execute(query)
        contact = result.scalars().first()

        if not contact:
            raise EntityNotFoundError("Target contact record was not found or already deleted.")

        # Stamping timezone-aware standard time signatures locks soft deletion state
        contact.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        logger.info(f"Contact entity soft-deleted successfully behind secure tracking ID: {contact_id}")
