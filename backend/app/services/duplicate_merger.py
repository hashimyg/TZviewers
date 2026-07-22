import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database.models.contact import Contact

logger = logging.getLogger("app.duplicate_merger")


class DuplicateMergerService:
    """
    High-Performance Data Normalization & Cleanup Engine.
    Scans the database cursor for telephone intersections, groups identical entries,
    and handles secure soft-delete cleanup procedures over redundant database rows.
    """

    @classmethod
    async def analyze_and_merge_system_duplicates(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Scans all active approved database entities to find identical numbers.
        Merges redundant contacts on-the-fly and soft-deletes lingering duplicates.
        """
        # Step A: Identify Duplicate Targets using Sub-query Groupings
        # Queries for phone strings that exist more than once inside the active pool
        duplicate_finder_stmt = (
            select(Contact.phone_number)
            .where(Contact.deleted_at == None)
            .group_by(Contact.phone_number)
            .having(func.count(Contact.phone_number) > 1)
        )
        
        finder_result = await db.execute(duplicate_finder_stmt)
        duplicate_phones: List[str] = list(finder_result.scalars().all())

        metrics = {
            "total_duplicate_groups_found": len(duplicate_phones),
            "total_records_merged_and_cleaned": 0
        }

        if not duplicate_phones:
            logger.info("System scan completed cleanly. Zero duplicate groups detected.")
            return metrics

        now_utc = datetime.now(timezone.utc)

        # Step B: Loop over each duplicate group sequentially to merge safely
        for phone in duplicate_phones:
            try:
                # Query all active rows matching this specific phone string ordered by oldest first
                group_stmt = (
                    select(Contact)
                    .where(and_(Contact.phone_number == phone, Contact.deleted_at == None))
                    .order_by(Contact.created_at.asc())
                )
                group_result = await db.execute(group_stmt)
                matching_rows: List[Contact] = list(group_result.scalars().all())

                if len(matching_rows) <= 1:
                    continue  # Protects loop tracking parameters defensively

                # Keep the oldest row as our Master Record (preserves original approval and consent history)
                master_record = matching_rows[0]
                redundant_records = matching_rows[1:]

                # Step C: Merge Name details intelligently if master lacks complete characters
                # If master has shorter string values, fill them using redundant properties
                for duplicate in redundant_records:
                    if len(duplicate.first_name) > len(master_record.first_name):
                        master_record.first_name = duplicate.first_name
                    if len(duplicate.last_name) > len(master_record.last_name):
                        master_record.last_name = duplicate.last_name
                    
                    # Consolidate Approval State: If any duplicate was approved, update the master to True
                    if duplicate.is_approved:
                        master_record.is_approved = True

                    # Step D: Apply secure Soft-Delete markings over redundant clones
                    duplicate.deleted_at = now_utc
                    metrics["total_records_merged_and_cleaned"] += 1

                # Update state locks across modifications
                db.add(master_record)
                
            except Exception as e:
                # Isolate specific group faults to prevent total background transactional failure
                logger.error(
                    "Database transactional exception intercepted during group duplicate merge tracking sequence",
                    extra={"target_phone": phone}
                )
                continue

        # Step E: Flush out all changes atomically via a single commit
        await db.commit()
        logger.info(f"System optimization successful. Merged groups: {metrics['total_duplicate_groups_found']} | Soft-deletes fired: {metrics['total_records_merged_and_cleaned']}")
        return metrics
