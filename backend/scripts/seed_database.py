"""
Database seeding script for development and testing.
Populates the database with sample musical works, users, and test data.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.db.session import async_session_maker, init_db
from app.models.catalog import CatalogUpload, UploadStatus
from app.models.user import User, UserRole
from app.models.works import (
    Contributor,
    ContributorRole,
    MusicalWork,
    Resource,
    ResourceType,
    RightsController,
)


async def create_users(session: AsyncSession) -> List[User]:
    """Create test users."""
    print("Creating users...")

    users = [
        User(
            email="admin@test.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN,
            is_active=True,
        ),
        User(
            email="publisher@test.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.PUBLISHER,
            is_active=True,
        ),
        User(
            email="publisher2@test.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.PUBLISHER,
            is_active=True,
        ),
    ]

    for user in users:
        # Check if user already exists
        statement = select(User).where(User.email == user.email)
        result = await session.execute(statement)
        existing = result.scalar_one_or_none()

        if not existing:
            session.add(user)
            print(f"  Created user: {user.email} (role: {user.role})")
        else:
            print(f"  User already exists: {user.email}")

    await session.commit()
    print(f"✓ Created {len(users)} users\n")
    return users


async def create_musical_works(session: AsyncSession) -> List[MusicalWork]:
    """Create sample musical works."""
    print("Creating musical works...")

    works_data = [
        {
            "title": "Bohemian Rhapsody",
            "alternate_titles": ["Bo Rhap"],
            "iswc": "T-070.244.478-1",
            "contributors": [
                {
                    "name": "Freddie Mercury",
                    "role": ContributorRole.COMPOSER,
                    "ipi_name_number": "00052210040",
                }
            ],
            "duration_seconds": 354,
            "year": 1975,
            "has_disputed_rights": False,
        },
        {
            "title": "Imagine",
            "alternate_titles": [],
            "iswc": "T-070.244.479-1",
            "contributors": [
                {"name": "John Lennon", "role": ContributorRole.COMPOSER},
                {"name": "Yoko Ono", "role": ContributorRole.COMPOSER},
            ],
            "duration_seconds": 183,
            "year": 1971,
            "has_disputed_rights": True,
        },
        {
            "title": "Let It Be",
            "alternate_titles": ["Let It Be (Single Version)"],
            "iswc": "T-070.244.480-1",
            "contributors": [
                {
                    "name": "Paul McCartney",
                    "role": ContributorRole.COMPOSER,
                    "ipi_name_number": "00052211070",
                }
            ],
            "duration_seconds": 243,
            "year": 1970,
            "has_disputed_rights": False,
        },
        {
            "title": "Stairway to Heaven",
            "alternate_titles": [],
            "iswc": "T-070.244.481-1",
            "contributors": [
                {"name": "Jimmy Page", "role": ContributorRole.COMPOSER},
                {"name": "Robert Plant", "role": ContributorRole.LYRICIST},
            ],
            "duration_seconds": 482,
            "year": 1971,
            "has_disputed_rights": False,
        },
        {
            "title": "Hotel California",
            "alternate_titles": [],
            "iswc": "T-070.244.482-1",
            "contributors": [
                {"name": "Don Felder", "role": ContributorRole.COMPOSER},
                {"name": "Don Henley", "role": ContributorRole.COMPOSER},
                {"name": "Glenn Frey", "role": ContributorRole.COMPOSER},
            ],
            "duration_seconds": 391,
            "year": 1976,
            "has_disputed_rights": False,
        },
        {
            "title": "Smells Like Teen Spirit",
            "alternate_titles": [],
            "iswc": "T-070.244.483-1",
            "contributors": [
                {"name": "Kurt Cobain", "role": ContributorRole.COMPOSER},
                {"name": "Krist Novoselic", "role": ContributorRole.COMPOSER},
                {"name": "Dave Grohl", "role": ContributorRole.COMPOSER},
            ],
            "duration_seconds": 301,
            "year": 1991,
            "has_disputed_rights": False,
        },
        {
            "title": "Billie Jean",
            "alternate_titles": [],
            "iswc": "T-070.244.484-1",
            "contributors": [
                {
                    "name": "Michael Jackson",
                    "role": ContributorRole.COMPOSER,
                    "ipi_name_number": "00052212090",
                }
            ],
            "duration_seconds": 294,
            "year": 1982,
            "has_disputed_rights": False,
        },
        {
            "title": "Like a Rolling Stone",
            "alternate_titles": [],
            "iswc": "T-070.244.485-1",
            "contributors": [
                {
                    "name": "Bob Dylan",
                    "role": ContributorRole.COMPOSER,
                    "ipi_name_number": "00052213100",
                }
            ],
            "duration_seconds": 369,
            "year": 1965,
            "has_disputed_rights": False,
        },
        {
            "title": "Hey Jude",
            "alternate_titles": [],
            "iswc": "T-070.244.486-1",
            "contributors": [
                {"name": "Paul McCartney", "role": ContributorRole.COMPOSER},
                {"name": "John Lennon", "role": ContributorRole.COMPOSER},
            ],
            "duration_seconds": 431,
            "year": 1968,
            "has_disputed_rights": False,
        },
        {
            "title": "Sweet Child O' Mine",
            "alternate_titles": ["Sweet Child of Mine"],
            "iswc": "T-070.244.487-1",
            "contributors": [
                {"name": "Slash", "role": ContributorRole.COMPOSER},
                {"name": "Axl Rose", "role": ContributorRole.LYRICIST},
                {"name": "Izzy Stradlin", "role": ContributorRole.COMPOSER},
            ],
            "duration_seconds": 356,
            "year": 1987,
            "has_disputed_rights": False,
        },
    ]

    works = []
    for work_data in works_data:
        # Check if work already exists
        statement = select(MusicalWork).where(MusicalWork.iswc == work_data["iswc"])
        result = await session.execute(statement)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Work already exists: {work_data['title']}")
            works.append(existing)
            continue

        # Create contributors
        contributors = []
        for contrib_data in work_data.pop("contributors"):
            contributor = Contributor(**contrib_data)
            contributors.append(contributor)

        # Create work
        work = MusicalWork(**work_data, contributors=contributors)
        session.add(work)
        works.append(work)
        print(f"  Created work: {work.title} ({work.iswc})")

    await session.commit()

    # Refresh to get IDs
    for work in works:
        await session.refresh(work)

    print(f"✓ Created {len(works)} musical works\n")
    return works


async def create_resources(session: AsyncSession, works: List[MusicalWork]) -> None:
    """Create sample resources for musical works."""
    print("Creating resources...")

    resources_data = [
        {
            "work_id": works[0].id,  # Bohemian Rhapsody
            "resource_type": ResourceType.MUSICBRAINZ,
            "resource_identifier": "mb-123456",
        },
        {
            "work_id": works[1].id,  # Imagine
            "resource_type": ResourceType.SPOTIFY,
            "resource_identifier": "spotify:track:7pKfPomDEeI4TPT6EOYjn9",
        },
        {
            "work_id": works[2].id,  # Let It Be
            "resource_type": ResourceType.MUSICBRAINZ,
            "resource_identifier": "mb-789012",
        },
    ]

    for resource_data in resources_data:
        resource = Resource(**resource_data)
        session.add(resource)
        print(f"  Created resource: {resource.resource_type} for work ID {resource.work_id}")

    await session.commit()
    print(f"✓ Created {len(resources_data)} resources\n")


async def create_rights_controllers(
    session: AsyncSession, works: List[MusicalWork]
) -> None:
    """Create sample rights controllers."""
    print("Creating rights controllers...")

    controllers_data = [
        {
            "work_id": works[0].id,  # Bohemian Rhapsody
            "controller_name": "Queen Productions Ltd",
            "society_affiliation": "PRS",
            "territory": "GB",
            "share_percentage": 100.0,
        },
        {
            "work_id": works[1].id,  # Imagine
            "controller_name": "Lenono Music",
            "society_affiliation": "BMI",
            "territory": "US",
            "share_percentage": 50.0,
        },
        {
            "work_id": works[1].id,  # Imagine
            "controller_name": "Ono Music",
            "society_affiliation": "BMI",
            "territory": "US",
            "share_percentage": 50.0,
        },
    ]

    for controller_data in controllers_data:
        controller = RightsController(**controller_data)
        session.add(controller)
        print(
            f"  Created rights controller: {controller.controller_name} "
            f"({controller.share_percentage}%)"
        )

    await session.commit()
    print(f"✓ Created {len(controllers_data)} rights controllers\n")


async def create_sample_uploads(session: AsyncSession, users: List[User]) -> None:
    """Create sample catalog uploads."""
    print("Creating sample uploads...")

    # Get publisher user
    publisher = next(u for u in users if u.role == UserRole.PUBLISHER)

    uploads_data = [
        {
            "user_id": publisher.id,
            "filename": "catalog_sample_1.csv",
            "publisher_name": "Universal Music Publishing",
            "file_format": "csv",
            "file_size_bytes": 1024000,
            "status": UploadStatus.COMPLETED,
            "tracks_count": 500,
            "progress_percentage": 100.0,
            "created_at": datetime.utcnow() - timedelta(days=7),
            "processing_stats": {
                "total_tracks": 500,
                "total_matches": 450,
                "high_confidence_matches": 300,
                "medium_confidence_matches": 100,
                "low_confidence_matches": 50,
                "processing_time_seconds": 45.2,
            },
        },
        {
            "user_id": publisher.id,
            "filename": "catalog_sample_2.xlsx",
            "publisher_name": "Sony Music Publishing",
            "file_format": "excel",
            "file_size_bytes": 2048000,
            "status": UploadStatus.COMPLETED,
            "tracks_count": 1000,
            "progress_percentage": 100.0,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "processing_stats": {
                "total_tracks": 1000,
                "total_matches": 920,
                "high_confidence_matches": 650,
                "medium_confidence_matches": 200,
                "low_confidence_matches": 70,
                "processing_time_seconds": 89.5,
            },
        },
        {
            "user_id": publisher.id,
            "filename": "catalog_sample_3.json",
            "publisher_name": "Warner Chappell Music",
            "file_format": "json",
            "file_size_bytes": 512000,
            "status": UploadStatus.FAILED,
            "tracks_count": 250,
            "progress_percentage": 45.0,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "status_message": "Processing error: Invalid track format at line 112",
        },
    ]

    for upload_data in uploads_data:
        upload = CatalogUpload(**upload_data)
        session.add(upload)
        print(
            f"  Created upload: {upload.filename} ({upload.status}) - "
            f"{upload.tracks_count} tracks"
        )

    await session.commit()
    print(f"✓ Created {len(uploads_data)} sample uploads\n")


async def seed_database():
    """Main seeding function."""
    print("=" * 60)
    print("BWARM Dashboard - Database Seeding")
    print("=" * 60)
    print()

    # Initialize database (create tables)
    await init_db()

    async with async_session_maker() as session:
        # Create data
        users = await create_users(session)
        works = await create_musical_works(session)
        await create_resources(session, works)
        await create_rights_controllers(session, works)
        await create_sample_uploads(session, users)

    print("=" * 60)
    print("✓ Database seeding completed successfully!")
    print("=" * 60)
    print()
    print("Test Users:")
    print("  Admin:     admin@test.com / password")
    print("  Publisher: publisher@test.com / password")
    print("  Publisher: publisher2@test.com / password")
    print()


if __name__ == "__main__":
    asyncio.run(seed_database())
