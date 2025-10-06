"""Elasticsearch search service for full-text search."""

from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from app.core.config import settings


class SearchService:
    """Elasticsearch search service for musical works."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.es: Optional[AsyncElasticsearch] = None
        self.index_name = "musical_works"

    async def connect(self):
        """Establish Elasticsearch connection."""
        if not self.es:
            self.es = AsyncElasticsearch(
                hosts=[settings.ELASTICSEARCH_URL],
                verify_certs=False,  # Disable for local development
            )

    async def disconnect(self):
        """Close Elasticsearch connection."""
        if self.es:
            await self.es.close()

    async def create_index(self):
        """Create Elasticsearch index with mapping."""
        if not self.es:
            await self.connect()

        # Define index mapping
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"},
                        },
                    },
                    "contributors": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "publisher": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "iswc": {"type": "keyword"},
                    "has_disputed_rights": {"type": "boolean"},
                    "created_at": {"type": "date"},
                    "search_text": {
                        "type": "text",
                        "analyzer": "english",
                    },
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "english_analyzer": {
                            "type": "standard",
                            "stopwords": "_english_",
                        }
                    }
                },
            },
        }

        try:
            # Check if index exists
            exists = await self.es.indices.exists(index=self.index_name)
            if not exists:
                # Create index
                await self.es.indices.create(index=self.index_name, body=mapping)
                print(f"Created Elasticsearch index: {self.index_name}")
            else:
                print(f"Index {self.index_name} already exists")
        except Exception as e:
            print(f"Error creating index: {e}")

    async def index_work(self, work: Dict[str, Any]):
        """Index a musical work document.

        Args:
            work: Dictionary with work data (id, title, contributors, etc.)
        """
        if not self.es:
            await self.connect()

        # Prepare document with combined search text
        doc = {
            "id": work.get("id"),
            "title": work.get("title", ""),
            "contributors": work.get("contributors", ""),
            "publisher": work.get("publisher", ""),
            "iswc": work.get("iswc"),
            "has_disputed_rights": work.get("has_disputed_rights", False),
            "created_at": work.get("created_at"),
            "search_text": f"{work.get('title', '')} {work.get('contributors', '')} {work.get('publisher', '')}",
        }

        try:
            await self.es.index(
                index=self.index_name, id=work.get("id"), document=doc
            )
        except Exception as e:
            print(f"Error indexing work {work.get('id')}: {e}")

    async def bulk_index_works(self, works: List[Dict[str, Any]]):
        """Bulk index multiple works.

        Args:
            works: List of work dictionaries
        """
        if not self.es:
            await self.connect()

        # Prepare bulk operations
        operations = []
        for work in works:
            operations.append({"index": {"_index": self.index_name, "_id": work.get("id")}})
            operations.append({
                "id": work.get("id"),
                "title": work.get("title", ""),
                "contributors": work.get("contributors", ""),
                "publisher": work.get("publisher", ""),
                "iswc": work.get("iswc"),
                "has_disputed_rights": work.get("has_disputed_rights", False),
                "created_at": work.get("created_at"),
                "search_text": f"{work.get('title', '')} {work.get('contributors', '')} {work.get('publisher', '')}",
            })

        try:
            response = await self.es.bulk(operations=operations)
            print(f"Bulk indexed {len(works)} works. Errors: {response.get('errors', False)}")
        except Exception as e:
            print(f"Error bulk indexing works: {e}")

    async def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        size: int = 20,
        from_: int = 0,
    ) -> Dict[str, Any]:
        """Full-text search for musical works.

        Args:
            query: Search query string
            filters: Optional filters (has_iswc, has_disputed_rights, etc.)
            size: Number of results to return
            from_: Offset for pagination

        Returns:
            Dictionary with search results and metadata
        """
        if not self.es:
            await self.connect()

        # Build search query
        must_clauses = []
        filter_clauses = []

        # Main search query
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "contributors^2", "publisher", "search_text"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            })

        # Apply filters
        if filters:
            if filters.get("has_iswc") is not None:
                if filters["has_iswc"]:
                    filter_clauses.append({"exists": {"field": "iswc"}})
                else:
                    filter_clauses.append({"bool": {"must_not": {"exists": {"field": "iswc"}}}})

            if filters.get("has_disputed_rights") is not None:
                filter_clauses.append({
                    "term": {"has_disputed_rights": filters["has_disputed_rights"]}
                })

        # Build final query
        es_query = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "contributors": {},
                    "publisher": {},
                }
            },
            "size": size,
            "from": from_,
        }

        try:
            response = await self.es.search(index=self.index_name, body=es_query)

            # Format results
            hits = response["hits"]["hits"]
            results = []
            for hit in hits:
                result = hit["_source"]
                result["_score"] = hit["_score"]
                if "highlight" in hit:
                    result["_highlight"] = hit["highlight"]
                results.append(result)

            return {
                "results": results,
                "total": response["hits"]["total"]["value"],
                "max_score": response["hits"]["max_score"],
            }
        except NotFoundError:
            # Index doesn't exist yet
            return {"results": [], "total": 0, "max_score": None}
        except Exception as e:
            print(f"Error searching: {e}")
            return {"results": [], "total": 0, "max_score": None, "error": str(e)}

    async def delete_work(self, work_id: int):
        """Delete a work from the index.

        Args:
            work_id: Work ID to delete
        """
        if not self.es:
            await self.connect()

        try:
            await self.es.delete(index=self.index_name, id=work_id)
        except NotFoundError:
            print(f"Work {work_id} not found in index")
        except Exception as e:
            print(f"Error deleting work {work_id}: {e}")

    async def reindex_all(self, works: List[Dict[str, Any]]):
        """Reindex all works (delete and recreate index).

        Args:
            works: List of all works to index
        """
        if not self.es:
            await self.connect()

        try:
            # Delete existing index
            await self.es.indices.delete(index=self.index_name, ignore=[404])
            print(f"Deleted index: {self.index_name}")

            # Recreate index
            await self.create_index()

            # Bulk index all works
            await self.bulk_index_works(works)
            print(f"Reindexed {len(works)} works")
        except Exception as e:
            print(f"Error reindexing: {e}")


# Global search service instance
search_service = SearchService()
