import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_admin
from app.database.models.admin import Admin
from app.services.upload_service import UploadService

logger = logging.getLogger("app.api.upload")
router = APIRouter(prefix="/upload", tags=["Bulk Upload Ingestion"])

ALLOWED_EXTENSIONS = {"vcf", "csv", "xlsx", "xls", "txt"}

@router.post("/bulk", status_code=status.HTTP_200_OK)
async def upload_bulk_contacts_ledger(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    logger.info(f"Bulk upload triggered by user: '{current_admin.username}'")
    filename = file.filename.lower() if file.filename else ""
    ext = filename.split(".")[-1] if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Security Alert: Unauthorized file extension '.{ext}'. System accepts CSV, Excel, TXT, or VCF only."
        )

    try:
        upload_batch = await UploadService.validate_and_stage_upload(file=file, db=db)
        inserted_rows = await UploadService.stream_and_ingest_bulk_file(db=db, upload_batch=upload_batch, file=file)
        return {
            "success": True,
            "message": f"Successfully processed '{file.filename}'! Imported {inserted_rows} fresh contacts into queue.",
            "records_found": upload_batch.total_records_found,
            "inserted_count": inserted_rows
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.critical(f"Unhandled ingestion exception caught: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
