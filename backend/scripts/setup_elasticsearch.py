"""
Elasticsearch index setup script.
Creates the musical_works index with proper mappings and analyzers.
Bulk indexes existing works from PostgreSQL.
"""
import asyncio
from typing import List

from elasticsearch import AsyncElasticsearch
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.session import async_session_maker
from app.models.works import MusicalWork


# Index mapping with custom analyzers
MUSICAL_WORKS_INDEX_MAPPING = {
    "settings": {
        "analysis": {
            "filter": {
                "music_synonym_filter": {
                    "type": "synonym",
                    "synonyms": [
                        "feat, featuring, ft",
                        "remix, rmx",
                        "original, orig",
                        "version, ver",
                        "edit, edited",
                        "instrumental, inst",
                        "vocal, vox",
                        "acoustic, unplugged",
                        "live, concert",
                        "studio, recorded",
                    ],
                },
                "music_stop_filter": {
                    "type": "stop",
                    "stopwords": ["the", "a", "an", "and", "or", "but"],
                },
            },
            "analyzer": {
                "music_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",  # Convert accented characters
                        "music_synonym_filter",
                        "music_stop_filter",
                    ],
                },
                "music_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "music_synonym_filter",
                    ],
                },
            },
        },
        "number_of_shards": 1,
        "number_of_replicas": 0,  # For development; use 1+ in production
    },
    "mappings": {
        "properties": {
            "work_id": {"type": "integer"},
            "title": {
                "type": "text",
                "analyzer": "music_analyzer",
                "search_analyzer": "music_search_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},  # Exact match
                    "ngram": {  # Partial match
                        "type": "text",
                        "analyzer": "standard",
                    },
                },
            },
            "alternate_titles": {
                "type": "text",
                "analyzer": "music_analyzer",
                "search_analyzer": "music_search_analyzer",
            },
            "iswc": {
                "type": "keyword",  # Exact match only
            },
            "contributors": {
                "type": "nested",
                "properties": {
                    "name": {
                        "type": "text",
                        "analyzer": "music_analyzer",
                        "search_analyzer": "music_search_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "role": {"type": "keyword"},
                    "ipi_name_number": {"type": "keyword"},
                },
            },
            "duration_seconds": {"type": "integer"},
            "year": {"type": "integer"},
            "has_disputed_rights": {"type": "boolean"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    },
}


async def create_index(es_client: AsyncElasticsearch, index_name: str) -> None:
    """Create the musical works index with mappings."""
    print(f"Creating index: {index_name}")

    # Check if index exists
    exists = await es_client.indices.exists(index=index_name)

    if exists:
        print(f"  Index {index_name} already exists")
        response = input("  Delete and recreate? (y/N): ")
        if response.lower() == "y":
            await es_client.indices.delete(index=index_name)
            print(f"  Deleted index {index_name}")
        else:
            print("  Keeping existing index")
            return

    # Create index
    await es_client.indices.create(index=index_name, body=MUSICAL_WORKS_INDEX_MAPPING)
    print(f"✓ Created index {index_name}")


async def index_works_from_db(
    es_client: AsyncElasticsearch, index_name: str, session: AsyncSession
) -> int:
    """Bulk index all works from PostgreSQL."""
    print("\nIndexing works from database...")

    # Fetch all works
    statement = select(MusicalWork)
    result = await session.execute(statement)
    works: List[MusicalWork] = list(result.scalars().all())

    if not works:
        print("  No works found in database")
        return 0

    print(f"  Found {len(works)} works to index")

    # Prepare bulk operations
    bulk_data = []
    for work in works:
        # Index operation
        bulk_data.append({"index": {"_index": index_name, "_id": str(work.id)}})

        # Document data
        doc = {
            "work_id": work.id,
            "title": work.title,
            "alternate_titles": work.alternate_titles or [],
            "iswc": work.iswc,
            "duration_seconds": work.duration_seconds,
            "year": work.year,
            "has_disputed_rights": work.has_disputed_rights,
            "created_at": work.created_at.isoformat() if work.created_at else None,
            "updated_at": work.updated_at.isoformat() if work.updated_at else None,
            "contributors": [],
        }

        # Add contributors
        if work.contributors:
            for contributor in work.contributors:
                doc["contributors"].append(
                    {
                        "name": contributor.name,
                        "role": contributor.role,
                        "ipi_name_number": contributor.ipi_name_number,
                    }
                )

        bulk_data.append(doc)

    # Perform bulk indexing
    response = await es_client.bulk(operations=bulk_data, refresh=True)

    # Check for errors
    if response.get("errors"):
        error_count = 0
        for item in response["items"]:
            if "error" in item.get("index", {}):
                error_count += 1
                print(f"  Error indexing document: {item['index']['error']}")

        print(f"  ⚠ Indexed {len(works) - error_count}/{len(works)} works (with errors)")
        return len(works) - error_count
    else:
        print(f"✓ Successfully indexed {len(works)} works")
        return len(works)


async def verify_index(es_client: AsyncElasticsearch, index_name: str) -> None:
    """Verify index creation and document count."""
    print("\nVerifying index...")

    # Get index stats
    stats = await es_client.indices.stats(index=index_name)
    doc_count = stats["indices"][index_name]["total"]["docs"]["count"]

    print(f"  Index: {index_name}")
    print(f"  Document count: {doc_count}")

    # Test search
    test_query = {"query": {"match_all": {}}, "size": 1}
    search_result = await es_client.search(index=index_name, body=test_query)

    if search_result["hits"]["total"]["value"] > 0:
        sample_doc = search_result["hits"]["hits"][0]["_source"]
        print(f"  Sample document: {sample_doc.get('title', 'N/A')}")
        print("✓ Index verification successful")
    else:
        print("  ⚠ No documents found in index")


async def setup_elasticsearch():
    """Main setup function."""
    print("=" * 60)
    print("BWARM Dashboard - Elasticsearch Setup")
    print("=" * 60)
    print()

    # Create Elasticsearch client
    es_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])

    try:
        # Check connection
        info = await es_client.info()
        print(f"Connected to Elasticsearch {info['version']['number']}")
        print(f"Cluster: {info['cluster_name']}")
        print()

        # Create index
        index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}musical_works"
        await create_index(es_client, index_name)

        # Index works from database
        async with async_session_maker() as session:
            indexed_count = await index_works_from_db(es_client, index_name, session)

        # Verify index
        if indexed_count > 0:
            await verify_index(es_client, index_name)

        print()
        print("=" * 60)
        print("✓ Elasticsearch setup completed successfully!")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    finally:
        await es_client.close()


if __name__ == "__main__":
    asyncio.run(setup_elasticsearch())
