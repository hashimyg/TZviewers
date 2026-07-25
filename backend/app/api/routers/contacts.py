import os
import uuid
import logging
from typing import Any, Dict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.dependencies.database import get_db
from app.database.models.admin import Admin
from app.database.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse
from app.dependencies.auth import get_current_admin

logger = logging.getLogger("app.api.contacts")
router = APIRouter(prefix="/contacts", tags=["Contact Ingestion Matrix"])

@router.post(
    "/submit",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Accepts public telephone ingestion parameters securely."
)
async def submit_public_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    logger.info("Public contact registration loop initiated.")
    
    existing_query = select(Contact).where(
        and_(Contact.phone_number == payload.phone_number, Contact.deleted_at == None)
    )
    result = await db.execute(existing_query)
    duplicate_record = result.scalars().first()

    if duplicate_record:
        logger.warning(f"Registration aborted: Phone number {payload.phone_number} is already taken.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This phone number is already registered inside our platform. Duplicate submissions are blocked."
        )

    resolved_last_name = payload.last_name.strip() if payload.last_name else payload.first_name.strip()

    new_contact = Contact(
        first_name=payload.first_name.strip(),
        last_name=resolved_last_name,
        phone_number=payload.phone_number,
        consent_given=payload.consent_given,
        is_approved=False,
        terms_version="v1.0"
    )

    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)

    logger.info(f"Success: Contact staged cleanly into pending logs pool. Record ID: {new_contact.id}")
    return {
        "success": True,
        "message": "Your profile was securely ingested. Information will go live once authorized by administrators."
    }

@router.get("/admin/list")
async def list_directory_records_for_admin(
    pending_only: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=100),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    logger.info(f"Administrative data stream audit called by Admin ID: {current_admin.id}")
    
    if pending_only:
        condition = and_(Contact.is_approved == False, Contact.deleted_at == None)
    else:
        condition = Contact.deleted_at == None
        
    query = select(Contact).where(condition).order_by(Contact.created_at.desc()).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()

    count_query = select(func.count(Contact.id)).where(condition)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0

    return {
        "success": True,
        "metrics": {"total_records": total_count},
        "data": [
            {
                "id": str(r.id),
                "first_name": r.first_name,
                "last_name": "" if r.last_name == r.first_name else r.last_name,
                "phone_number": r.phone_number,
                "is_approved": r.is_approved,
                "terms_version": r.terms_version
            } for r in records
        ]
    }

@router.patch("/admin/{contact_id}/approve", status_code=status.HTTP_200_OK)
async def authorize_pending_contact(
    contact_id: uuid.UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    query = select(Contact).where(and_(Contact.id == contact_id, Contact.deleted_at == None))
    result = await db.execute(query)
    contact = result.scalars().first()

    if not contact:
        return {"success": False, "message": "Target logging row not found inside active records indices."}

    contact.is_approved = True
    await db.commit()
    logger.info(f"Record row approved securely by Admin profile token: {current_admin.id}")
    return {"success": True, "message": "Contact entry successfully verified and added to public master loops."}

@router.delete("/admin/{contact_id}", status_code=status.HTTP_200_OK)
async def soft_delete_directory_record(
    contact_id: uuid.UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    query = select(Contact).where(and_(Contact.id == contact_id, Contact.deleted_at == None))
    result = await db.execute(query)
    contact = result.scalars().first()

    if not contact:
        return {"success": False, "message": "Target logging row not found inside active records indices."}

    contact.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    logger.info(f"Record row soft deleted by Admin profile token: {current_admin.id}")
    return {"success": True, "message": "Contact entry successfully purged from database scopes."}

@router.post("/vcf/generate")
async def trigger_vcf_generation(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    from app.services.vcf_engine import VcfEngineService
    try:
        await VcfEngineService.compile_master_vcf(db=db)
        return {"success": True, "message": "Master vCard directory file assembled completely."}
    except Exception as e:
        logger.error(f"VCF Generation error: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Compilation collapsed: {str(e)}"}

@router.get("/vcf/download")
async def download_master_vcf_file(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse
    from app.services.vcf_engine import VcfEngineService, MASTER_VCF_PATH
    
    try:
        admin = await get_current_admin(token=token, db=db)
    except Exception:
         raise HTTPException(status_code=401, detail="Unauthorized access token sequence.")
         
    try:
        await VcfEngineService.compile_master_vcf(db=db)
    except Exception as e:
        logger.error(f"Assembly failed during download request: {str(e)}")

    if not MASTER_VCF_PATH.exists():
         raise HTTPException(status_code=404, detail="Assembled directory target log file is missing.")
         
    return FileResponse(
        path=str(MASTER_VCF_PATH), 
        filename="Master_Contacts_Verified.vcf", 
        media_type="text/vcard"
    )

@router.get("/admin/trash", summary="Lists all soft-deleted records for recovery.")
async def list_deleted_contacts(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(Contact).where(Contact.deleted_at != None).order_by(Contact.deleted_at.desc())
    res = await db.execute(query)
    records = res.scalars().all()
    return {"success": True, "data": [{"id": str(r.id), "first_name": r.first_name, "last_name": r.last_name, "phone_number": r.phone_number} for r in records]}

@router.patch("/admin/{contact_id}/restore", summary="Restores a soft-deleted contact record row.")
async def restore_deleted_contact(
    contact_id: uuid.UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(Contact).where(Contact.id == contact_id)
    res = await db.execute(query)
    contact = res.scalars().first()
    if not contact:
        return {"success": False, "message": "Record not found."}
    
    contact.deleted_at = None
    contact.is_approved = False
    await db.commit()
    return {"success": True, "message": "Contact restored safely down into validation loops!"}

# =====================================================================
# PERMANENT PURGE (HARD DELETE) ENDPOINT
# =====================================================================
@router.delete("/admin/{contact_id}/purge", status_code=status.HTTP_200_OK, summary="Permanently deletes a contact from the database.")
async def purge_contact_permanently(
    contact_id: uuid.UUID,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Hard delete operation: Removes the target contact record permanently from PostgreSQL database.
    """
    query = select(Contact).where(Contact.id == contact_id)
    res = await db.execute(query)
    contact = res.scalars().first()

    if not contact:
        return {"success": False, "message": "Target contact record not found inside database registry."}

    await db.delete(contact)
    await db.commit()

    logger.info(f"Contact ID {contact_id} permanently purged from database by Admin ID: {current_admin.id}")

    return {
        "success": True,
        "message": "Contact record permanently purged from database.",
        "purged_id": str(contact_id)
    }