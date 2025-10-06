"""Elasticsearch integration service for full-text search."""

import logging
from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk

from app.core.config import settings
from app.models.musical_work import MusicalWork

logger = logging.getLogger(__name__)


class SearchService:
    """Elasticsearch service for music metadata search."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client: Optional[AsyncElasticsearch] = None
        self.index_name = "musical_works"

    async def connect(self):
        """Connect to Elasticsearch cluster."""
        try:
            self.client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
            await self.client.ping()
            logger.info("Elasticsearch connection established")

            # Create index if it doesn't exist
            await self._create_index_if_not_exists()

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            self.client = None

    async def disconnect(self):
        """Close Elasticsearch connection."""
        if self.client:
            await self.client.close()
            logger.info("Elasticsearch connection closed")

    async def _create_index_if_not_exists(self):
        """Create index with proper mappings if it doesn't exist."""
        if not self.client:
            return

        try:
            exists = await self.client.indices.exists(index=self.index_name)
            if not exists:
                await self.client.indices.create(
                    index=self.index_name,
                    body={
                        "settings": {
                            "analysis": {
                                "analyzer": {
                                    "music_analyzer": {
                                        "type": "custom",
                                        "tokenizer": "standard",
                                        "filter": [
                                            "lowercase",
                                            "asciifolding",
                                            "music_synonym",
                                        ],
                                    }
                                },
                                "filter": {
                                    "music_synonym": {
                                        "type": "synonym",
                                        "synonyms": [
                                            "feat, featuring, ft",
                                            "vs, versus",
                                            "remix, rmx",
                                        ],
                                    }
                                },
                            }
                        },
                        "mappings": {
                            "properties": {
                                "title": {
                                    "type": "text",
                                    "analyzer": "music_analyzer",
                                    "fields": {"keyword": {"type": "keyword"}},
                                },
                                "alternate_titles": {
                                    "type": "text",
                                    "analyzer": "music_analyzer",
                                },
                                "iswc": {"type": "keyword"},
                                "contributors": {
                                    "type": "nested",
                                    "properties": {
                                        "name": {
                                            "type": "text",
                                            "analyzer": "music_analyzer",
                                        },
                                        "role": {"type": "keyword"},
                                    },
                                },
                                "lyrics_languages": {"type": "keyword"},
                                "country_of_production": {"type": "keyword"},
                                "has_disputed_rights": {"type": "boolean"},
                                "created_at": {"type": "date"},
                            }
                        },
                    },
                )
                logger.info(f"Created index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")

    async def index_work(self, work: MusicalWork) -> bool:
        """Index a single musical work.

        Args:
            work: MusicalWork to index

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Elasticsearch not available, skipping indexing")
            return False

        try:
            # Convert work to document
            doc = {
                "title": work.title,
                "alternate_titles": work.alternate_titles or [],
                "iswc": work.iswc,
                "contributors": work.contributors or [],
                "lyrics_languages": work.lyrics_languages or [],
                "country_of_production": work.country_of_production,
                "has_disputed_rights": work.has_disputed_rights,
                "created_at": work.created_at.isoformat() if work.created_at else None,
            }

            await self.client.index(index=self.index_name, id=str(work.id), body=doc)
            logger.debug(f"Indexed work {work.id}: {work.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to index work {work.id}: {e}")
            return False

    async def bulk_index_works(self, works: List[MusicalWork]) -> int:
        """Bulk index multiple works.

        Args:
            works: List of MusicalWork to index

        Returns:
            Number of successfully indexed works
        """
        if not self.client or not works:
            return 0

        try:
            # Prepare bulk actions
            actions = []
            for work in works:
                doc = {
                    "_index": self.index_name,
                    "_id": str(work.id),
                    "_source": {
                        "title": work.title,
                        "alternate_titles": work.alternate_titles or [],
                        "iswc": work.iswc,
                        "contributors": work.contributors or [],
                        "lyrics_languages": work.lyrics_languages or [],
                        "country_of_production": work.country_of_production,
                        "has_disputed_rights": work.has_disputed_rights,
                        "created_at": (
                            work.created_at.isoformat() if work.created_at else None
                        ),
                    },
                }
                actions.append(doc)

            # Execute bulk operation
            success, failed = await async_bulk(
                self.client, actions, raise_on_error=False
            )

            logger.info(f"Bulk indexed {success} works, {len(failed)} failed")
            return success

        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return 0

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for musical works.

        Args:
            query: Search query string
            filters: Additional filters (has_iswc, has_disputed_rights, etc.)

        Returns:
            List of search results with scores
        """
        if not self.client:
            logger.warning("Elasticsearch not available, returning empty results")
            return []

        try:
            # Build query
            must_clauses = []

            # Multi-match query across title and contributors
            if query:
                must_clauses.append(
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "title^3",
                                "alternate_titles^2",
                                "contributors.name",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                        }
                    }
                )

            # Apply filters
            filter_clauses = []
            if filters:
                if "has_iswc" in filters:
                    filter_clauses.append(
                        {"exists": {"field": "iswc"}}
                        if filters["has_iswc"]
                        else {"bool": {"must_not": {"exists": {"field": "iswc"}}}}
                    )

                if "has_disputed_rights" in filters:
                    filter_clauses.append(
                        {"term": {"has_disputed_rights": filters["has_disputed_rights"]}}
                    )

                if "country_of_production" in filters:
                    filter_clauses.append(
                        {"term": {"country_of_production": filters["country_of_production"]}}
                    )

            # Construct final query
            search_query: Dict[str, Any] = {"bool": {}}
            if must_clauses:
                search_query["bool"]["must"] = must_clauses
            if filter_clauses:
                search_query["bool"]["filter"] = filter_clauses

            # Execute search
            response = await self.client.search(
                index=self.index_name, body={"query": search_query, "size": 100}
            )

            # Format results
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["id"] = int(hit["_id"])
                result["search_score"] = hit["_score"]
                results.append(result)

            logger.debug(f"Search for '{query}' returned {len(results)} results")
            return results

        except NotFoundError:
            logger.warning(f"Index {self.index_name} not found")
            return []
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_work(self, work_id: int) -> bool:
        """Delete a work from the index.

        Args:
            work_id: ID of work to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            await self.client.delete(index=self.index_name, id=str(work_id))
            logger.debug(f"Deleted work {work_id} from index")
            return True
        except NotFoundError:
            logger.warning(f"Work {work_id} not found in index")
            return False
        except Exception as e:
            logger.error(f"Failed to delete work {work_id}: {e}")
            return False


# Global service instance
search_service = SearchService()
