import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.contact import Contact

logger = logging.getLogger("app.services.vcf_engine")

# Njia ya asili ambapo faili la Master VCF linahifadhiwa kwenye diski
STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "vcf"
MASTER_VCF_PATH = STORAGE_DIR / "master_directory.vcf"

class VcfEngineService:
    """
    Industrial Asynchronous VCF Card Export Matrix Loops.
    Compiles database rows into standardized vCard 3.0 cellular formats.
    """

    @classmethod
    # FIXED: Jina limebadilishwa kuwa compile_master_vcf ili kuondoa AttributeNotFound Error!
    async def compile_master_vcf(cls, db: AsyncSession) -> int:
        logger.info("Master vCard compilation sequence initiated by administrative request.")
        
        # 1. Hakikisha folda la kuhifadhia faili lipo kwenye diski
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        try:
            # 2. Vuta namba zote zilizoidhinishwa (is_approved=True) na ambazo hazijafutwa
            stmt = select(Contact).where(
                and_(Contact.is_approved == True, Contact.deleted_at == None)
            ).order_by(Contact.first_name.asc())
            
            result = await db.execute(stmt)
            approved_contacts: List[Contact] = list(result.scalars().all())

            # 3. Anza kuandika faili la VCF upya (Master Accumulative Overwrite)
            with open(MASTER_VCF_PATH, "w", encoding="utf-8") as vcf_file:
                for contact in approved_contacts:
                    vcf_file.write("BEGIN:VCARD\n")
                    vcf_file.write("VERSION:3.0\n")
                    
                    # Unganisha jina la kwanza na la pili
                    full_name = f"{contact.first_name} {contact.last_name}".strip()
                    vcf_file.write(f"FN:{full_name}\n")
                    vcf_file.write(f"N:{contact.last_name};{contact.first_name};;;\n")
                    
                    # FIXED: Alama ya dollar ($) imeondolewa ili namba isafishike kiwanda
                    vcf_file.write(f"TEL;TYPE=CELL:{contact.phone_number}\n")
                    vcf_file.write("END:VCARD\n")

            total_compiled = len(approved_contacts)
            logger.info(f"SUCCESS: Master vCard ledger closed cleanly. Injected {total_compiled} records into disk pipeline.")
            return total_compiled

        except Exception as e:
            logger.error(f"Matrix compilation loop failed: {str(e)}", exc_info=True)
            raise e
