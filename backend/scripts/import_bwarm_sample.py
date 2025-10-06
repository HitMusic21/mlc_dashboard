"""Import BWARM sample data into the database.

This script parses and imports The MLC's BWARM 2.0 sample data into the BWARM Dashboard database.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, init_db
from app.models.musical_work import MusicalWork
from app.services.parsers.bwarm_tsv_parser import BWARMTSVParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def import_musical_works(session: AsyncSession, works: list, parties_map: dict, shares: list):
    """Import musical works with contributor information from right shares.

    Args:
        session: Database session
        works: List of musical work dictionaries from parser
        parties_map: Dictionary mapping party record IDs to party names
        shares: List of right share dictionaries
    """
    # Build a map of work record ID to composers
    work_composers = {}
    work_publishers = {}

    for share in shares:
        work_id = share["musical_work_record_id"]
        party_id = share["party_record_id"]
        role = share["party_role"]

        party_name = parties_map.get(party_id, "Unknown")

        if role == "Composer":
            if work_id not in work_composers:
                work_composers[work_id] = []
            work_composers[work_id].append(party_name)
        elif role in ["OriginalPublisher", "RightsAdministrator"]:
            if work_id not in work_publishers:
                work_publishers[work_id] = []
            work_publishers[work_id].append(party_name)

    imported = 0
    skipped = 0

    for work_data in works:
        record_id = work_data["record_id"]
        title = work_data["title"]

        # Check if work already exists
        result = await session.execute(
            select(MusicalWork).where(MusicalWork.title == title)
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"Skipping existing work: {title}")
            skipped += 1
            continue

        # Build contributors string
        composers = work_composers.get(record_id, [])
        contributors_str = ", ".join(composers) if composers else None

        # Build publisher string
        publishers = work_publishers.get(record_id, [])
        publisher_str = publishers[0] if publishers else None

        # Create musical work
        work = MusicalWork(
            title=title,
            iswc=work_data["iswc"],
            contributors=contributors_str,
            publisher=publisher_str,
            territory="US",  # Sample data is all US territory
            has_disputed_rights=work_data["has_right_share_in_dispute"],
        )

        session.add(work)
        imported += 1

        if imported % 100 == 0:
            await session.flush()
            logger.info(f"Imported {imported} works...")

    await session.commit()
    logger.info(f"Import complete: {imported} works imported, {skipped} skipped")


async def main():
    """Main import function."""
    # Parse BWARM sample data
    sample_data_path = "/Users/carlosmescalona/Downloads/Sample Data"

    logger.info("=" * 80)
    logger.info("BWARM Sample Data Import")
    logger.info("=" * 80)

    # Initialize parser
    parser = BWARMTSVParser(sample_data_path)

    # Parse all data
    logger.info(f"Parsing BWARM data from: {sample_data_path}")
    data = parser.parse_all()

    # Create parties lookup map
    parties_map = {p["record_id"]: p["full_name"] for p in data["parties"]}

    logger.info("\nParsed BWARM Data Summary:")
    logger.info(f"  - Musical Works: {len(data['musical_works'])}")
    logger.info(f"  - Parties (Composers/Publishers): {len(data['parties'])}")
    logger.info(f"  - Right Shares: {len(data['musical_work_right_shares'])}")
    logger.info(f"  - Alternative Titles: {len(data['alternative_musical_work_titles'])}")
    logger.info(f"  - Work Identifiers: {len(data['musical_work_identifiers'])}")

    # Initialize database
    logger.info("\nInitializing database...")
    await init_db()

    # Import data
    logger.info("\nImporting musical works...")
    async with AsyncSessionLocal() as session:
        await import_musical_works(
            session,
            data["musical_works"],
            parties_map,
            data["musical_work_right_shares"],
        )

    logger.info("\n" + "=" * 80)
    logger.info("Import completed successfully!")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
