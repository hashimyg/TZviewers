import os
import logging
from pathlib import Path
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.contact import Contact

logger = logging.getLogger("app.services.vcf_engine")

class VcfEngineService:
    STORAGE_DIR = Path("/app/storage/vcf")

    @classmethod
    def initialize_storage_environment(cls):
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)

    @classmethod
    async def compile_master_vcf(cls, db: AsyncSession) -> str:
        cls.initialize_storage_environment()
        output_file_path = cls.STORAGE_DIR / "master_directory.vcf"
        
        query = select(Contact).where(
            and_(
                Contact.is_approved == True,
                Contact.deleted_at == None
            )
        )
        result = await db.execute(query)
        records = result.scalars().all()

        logger.info(f"VCF Compiler pulling data: Compiling {len(records)} verified profile registers.")

        with open(output_file_path, "w", encoding="utf-8") as vcf_file:
            for idx, contact in enumerate(records, start=1):
                # 🧼 FIXED SANITIZATION LAYER: Kama jina la pili ni mkwaju au linafanana na la kwanza, tunaliacha tupu
                f_name = contact.first_name.strip()
                l_name = contact.last_name.strip() if contact.last_name else ""
                
                if l_name == "-" or l_name == f_name:
                    full_name = f_name
                    n_field = f";{f_name};;;"
                else:
                    full_name = f"{f_name} {l_name}".strip()
                    n_field = f"{l_name};{f_name};;;"
                
                # Jenga muundo rasmi wa kimataifa wa vCard 3.0 Standard Specs
                vcf_file.write("BEGIN:VCARD\n")
                vcf_file.write("VERSION:3.0\n")
                vcf_file.write(f"FN:{full_name}\n")
                vcf_file.write(f"N:{n_field}\n")
                vcf_file.write(f"TEL;TYPE=CELL;TYPE=PREF:{contact.phone_number}\n")
                vcf_file.write("END:VCARD\n")

        logger.info("SUCCESS: Master VCF assembly file generation matrix compiled cleanly.")
        return str(output_file_path)
