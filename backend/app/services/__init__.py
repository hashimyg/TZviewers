from app.services.auth_service import AuthService
from app.services.contact_service import ContactService
from app.services.upload_service import UploadService
from app.services.vcf_engine import VcfEngineService
from app.services.duplicate_merger import DuplicateMergerService  # FIXED: Tumeondoa ile `.py` ya mwisho

__all__ = [
    "AuthService",
    "ContactService",
    "UploadService",
    "VcfEngineService",
    "DuplicateMergerService"
]
