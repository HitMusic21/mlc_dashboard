"""Unit tests for Elasticsearch search service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from elasticsearch import NotFoundError

from app.services.search_service import SearchService


@pytest.fixture
def search_service():
    """Create a fresh SearchService instance for each test."""
    service = SearchService()
    return service


@pytest.fixture
def mock_es_client():
    """Create a mock Elasticsearch client."""
    mock_client = AsyncMock()

    # Mock indices operations
    mock_client.indices = AsyncMock()
    mock_client.indices.exists = AsyncMock(return_value=False)
    mock_client.indices.create = AsyncMock()
    mock_client.indices.delete = AsyncMock()

    # Mock document operations
    mock_client.index = AsyncMock()
    mock_client.delete = AsyncMock()
    mock_client.bulk = AsyncMock(return_value={"errors": False})

    # Mock search
    mock_client.search = AsyncMock(return_value={
        "hits": {
            "hits": [],
            "total": {"value": 0},
            "max_score": None
        }
    })

    # Mock close
    mock_client.close = AsyncMock()

    return mock_client


class TestSearchServiceConnection:
    """Test Elasticsearch connection management."""

    @pytest.mark.asyncio
    async def test_connect_creates_client(self, search_service):
        """Test that connect() creates an Elasticsearch client."""
        with patch("app.services.search_service.AsyncElasticsearch") as mock_es:
            mock_es.return_value = AsyncMock()

            await search_service.connect()

            assert search_service.es is not None
            mock_es.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_uses_settings_url(self, search_service):
        """Test that connect() uses the configured Elasticsearch URL."""
        with patch("app.services.search_service.AsyncElasticsearch") as mock_es:
            with patch("app.services.search_service.settings") as mock_settings:
                mock_settings.ELASTICSEARCH_URL = "http://test-es:9200"
                mock_es.return_value = AsyncMock()

                await search_service.connect()

                mock_es.assert_called_once_with(
                    hosts=["http://test-es:9200"],
                    verify_certs=False
                )

    @pytest.mark.asyncio
    async def test_disconnect_closes_client(self, search_service, mock_es_client):
        """Test that disconnect() closes the Elasticsearch client."""
        search_service.es = mock_es_client

        await search_service.disconnect()

        mock_es_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_handles_none_client(self, search_service):
        """Test that disconnect() handles None client gracefully."""
        search_service.es = None

        # Should not raise an error
        await search_service.disconnect()


class TestIndexManagement:
    """Test Elasticsearch index management."""

    @pytest.mark.asyncio
    async def test_create_index_when_not_exists(self, search_service, mock_es_client):
        """Test index creation when index doesn't exist."""
        search_service.es = mock_es_client
        mock_es_client.indices.exists.return_value = False

        await search_service.create_index()

        mock_es_client.indices.exists.assert_called_once_with(index="musical_works")
        mock_es_client.indices.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_index_when_exists(self, search_service, mock_es_client):
        """Test that create_index() skips creation if index exists."""
        search_service.es = mock_es_client
        mock_es_client.indices.exists.return_value = True

        await search_service.create_index()

        mock_es_client.indices.exists.assert_called_once()
        mock_es_client.indices.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_index_mapping_structure(self, search_service, mock_es_client):
        """Test that index mapping has correct structure."""
        search_service.es = mock_es_client
        mock_es_client.indices.exists.return_value = False

        await search_service.create_index()

        # Get the mapping that was passed to create
        call_args = mock_es_client.indices.create.call_args
        mapping = call_args.kwargs["body"]

        # Verify key mapping fields
        assert "mappings" in mapping
        assert "properties" in mapping["mappings"]
        props = mapping["mappings"]["properties"]

        assert "title" in props
        assert props["title"]["type"] == "text"
        assert "keyword" in props["title"]["fields"]
        assert "suggest" in props["title"]["fields"]

        assert "contributors" in props
        assert "publisher" in props
        assert "iswc" in props
        assert props["iswc"]["type"] == "keyword"
        assert "has_disputed_rights" in props
        assert props["has_disputed_rights"]["type"] == "boolean"

    @pytest.mark.asyncio
    async def test_create_index_connects_if_needed(self, search_service):
        """Test that create_index() connects if client is None."""
        assert search_service.es is None

        with patch.object(search_service, "connect", new_callable=AsyncMock) as mock_connect:
            # Setup mock client that will be set by connect()
            mock_es = AsyncMock()
            mock_es.indices = AsyncMock()
            mock_es.indices.exists = AsyncMock(return_value=True)

            async def set_client():
                search_service.es = mock_es

            mock_connect.side_effect = set_client

            await search_service.create_index()

            mock_connect.assert_called_once()


class TestDocumentIndexing:
    """Test document indexing operations."""

    @pytest.mark.asyncio
    async def test_index_work_basic(self, search_service, mock_es_client):
        """Test indexing a single work."""
        search_service.es = mock_es_client

        work_data = {
            "id": 1,
            "title": "Test Work",
            "contributors": "Test Artist",
            "publisher": "Test Publisher",
            "iswc": "T-123.456.789-0",
            "has_disputed_rights": False,
            "created_at": "2025-01-15T10:00:00Z"
        }

        await search_service.index_work(work_data)

        mock_es_client.index.assert_called_once()
        call_args = mock_es_client.index.call_args

        assert call_args.kwargs["index"] == "musical_works"
        assert call_args.kwargs["id"] == 1

        doc = call_args.kwargs["document"]
        assert doc["title"] == "Test Work"
        assert doc["contributors"] == "Test Artist"
        assert "search_text" in doc
        assert "Test Work" in doc["search_text"]

    @pytest.mark.asyncio
    async def test_index_work_search_text_combination(self, search_service, mock_es_client):
        """Test that search_text combines title, contributors, and publisher."""
        search_service.es = mock_es_client

        work_data = {
            "id": 1,
            "title": "Symphony No. 9",
            "contributors": "Beethoven",
            "publisher": "Universal Music",
            "iswc": None,
            "has_disputed_rights": False,
        }

        await search_service.index_work(work_data)

        doc = mock_es_client.index.call_args.kwargs["document"]
        assert doc["search_text"] == "Symphony No. 9 Beethoven Universal Music"

    @pytest.mark.asyncio
    async def test_index_work_handles_missing_fields(self, search_service, mock_es_client):
        """Test that index_work() handles missing optional fields."""
        search_service.es = mock_es_client

        work_data = {"id": 1}  # Minimal data

        await search_service.index_work(work_data)

        doc = mock_es_client.index.call_args.kwargs["document"]
        assert doc["title"] == ""
        assert doc["contributors"] == ""
        assert doc["publisher"] == ""
        assert doc["iswc"] is None
        assert doc["has_disputed_rights"] is False

    @pytest.mark.asyncio
    async def test_bulk_index_works(self, search_service, mock_es_client):
        """Test bulk indexing multiple works."""
        search_service.es = mock_es_client

        works_data = [
            {"id": 1, "title": "Work 1", "contributors": "Artist 1", "publisher": "Pub 1"},
            {"id": 2, "title": "Work 2", "contributors": "Artist 2", "publisher": "Pub 2"},
            {"id": 3, "title": "Work 3", "contributors": "Artist 3", "publisher": "Pub 3"},
        ]

        await search_service.bulk_index_works(works_data)

        mock_es_client.bulk.assert_called_once()

        # Verify bulk operations format
        operations = mock_es_client.bulk.call_args.kwargs["operations"]

        # Should have 6 operations (2 per work: index action + document)
        assert len(operations) == 6

        # Verify first work
        assert operations[0] == {"index": {"_index": "musical_works", "_id": 1}}
        assert operations[1]["id"] == 1
        assert operations[1]["title"] == "Work 1"

    @pytest.mark.asyncio
    async def test_bulk_index_empty_list(self, search_service, mock_es_client):
        """Test bulk indexing with empty list."""
        search_service.es = mock_es_client

        await search_service.bulk_index_works([])

        mock_es_client.bulk.assert_called_once()
        operations = mock_es_client.bulk.call_args.kwargs["operations"]
        assert len(operations) == 0


class TestSearchOperations:
    """Test search functionality."""

    @pytest.mark.asyncio
    async def test_search_basic_query(self, search_service, mock_es_client):
        """Test basic search query."""
        search_service.es = mock_es_client

        await search_service.search(query="beethoven", size=20, from_=0)

        mock_es_client.search.assert_called_once()

        call_args = mock_es_client.search.call_args
        assert call_args.kwargs["index"] == "musical_works"

        es_query = call_args.kwargs["body"]
        assert es_query["size"] == 20
        assert es_query["from"] == 0

    @pytest.mark.asyncio
    async def test_search_multi_match_configuration(self, search_service, mock_es_client):
        """Test that search uses multi_match with correct fields and boosting."""
        search_service.es = mock_es_client

        await search_service.search(query="symphony")

        es_query = mock_es_client.search.call_args.kwargs["body"]
        multi_match = es_query["query"]["bool"]["must"][0]["multi_match"]

        assert multi_match["query"] == "symphony"
        assert "title^3" in multi_match["fields"]
        assert "contributors^2" in multi_match["fields"]
        assert "publisher" in multi_match["fields"]
        assert multi_match["type"] == "best_fields"
        assert multi_match["fuzziness"] == "AUTO"

    @pytest.mark.asyncio
    async def test_search_with_iswc_filter(self, search_service, mock_es_client):
        """Test search with has_iswc filter."""
        search_service.es = mock_es_client

        await search_service.search(
            query="beethoven",
            filters={"has_iswc": True}
        )

        es_query = mock_es_client.search.call_args.kwargs["body"]
        filter_clauses = es_query["query"]["bool"]["filter"]

        assert len(filter_clauses) == 1
        assert "exists" in filter_clauses[0]
        assert filter_clauses[0]["exists"]["field"] == "iswc"

    @pytest.mark.asyncio
    async def test_search_without_iswc_filter(self, search_service, mock_es_client):
        """Test search filtering works without ISWC."""
        search_service.es = mock_es_client

        await search_service.search(
            query="beethoven",
            filters={"has_iswc": False}
        )

        es_query = mock_es_client.search.call_args.kwargs["body"]
        filter_clauses = es_query["query"]["bool"]["filter"]

        assert len(filter_clauses) == 1
        assert "bool" in filter_clauses[0]
        assert "must_not" in filter_clauses[0]["bool"]

    @pytest.mark.asyncio
    async def test_search_with_disputed_rights_filter(self, search_service, mock_es_client):
        """Test search with disputed rights filter."""
        search_service.es = mock_es_client

        await search_service.search(
            query="beethoven",
            filters={"has_disputed_rights": True}
        )

        es_query = mock_es_client.search.call_args.kwargs["body"]
        filter_clauses = es_query["query"]["bool"]["filter"]

        assert len(filter_clauses) == 1
        assert filter_clauses[0] == {"term": {"has_disputed_rights": True}}

    @pytest.mark.asyncio
    async def test_search_with_multiple_filters(self, search_service, mock_es_client):
        """Test search with multiple filters combined."""
        search_service.es = mock_es_client

        await search_service.search(
            query="beethoven",
            filters={"has_iswc": True, "has_disputed_rights": False}
        )

        es_query = mock_es_client.search.call_args.kwargs["body"]
        filter_clauses = es_query["query"]["bool"]["filter"]

        # Should have 2 filter clauses
        assert len(filter_clauses) == 2

    @pytest.mark.asyncio
    async def test_search_highlighting_configuration(self, search_service, mock_es_client):
        """Test that search includes highlighting configuration."""
        search_service.es = mock_es_client

        await search_service.search(query="beethoven")

        es_query = mock_es_client.search.call_args.kwargs["body"]
        highlight = es_query["highlight"]

        assert "fields" in highlight
        assert "title" in highlight["fields"]
        assert "contributors" in highlight["fields"]
        assert "publisher" in highlight["fields"]

    @pytest.mark.asyncio
    async def test_search_response_formatting(self, search_service, mock_es_client):
        """Test that search results are properly formatted."""
        search_service.es = mock_es_client

        mock_es_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {"id": 1, "title": "Work 1"},
                        "_score": 10.5,
                        "highlight": {"title": ["<em>Work</em> 1"]}
                    }
                ],
                "total": {"value": 1},
                "max_score": 10.5
            }
        }

        result = await search_service.search(query="work")

        assert result["total"] == 1
        assert result["max_score"] == 10.5
        assert len(result["results"]) == 1

        first_result = result["results"][0]
        assert first_result["id"] == 1
        assert first_result["_score"] == 10.5
        assert first_result["_highlight"] == {"title": ["<em>Work</em> 1"]}

    @pytest.mark.asyncio
    async def test_search_index_not_found(self, search_service, mock_es_client):
        """Test search when index doesn't exist."""
        search_service.es = mock_es_client

        # Create proper NotFoundError with required parameters
        error = NotFoundError(
            message="index_not_found_exception",
            meta=MagicMock(),
            body={}
        )
        mock_es_client.search.side_effect = error

        result = await search_service.search(query="beethoven")

        assert result["results"] == []
        assert result["total"] == 0
        assert result["max_score"] is None

    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_service, mock_es_client):
        """Test search error handling for general exceptions."""
        search_service.es = mock_es_client
        mock_es_client.search.side_effect = Exception("Connection error")

        result = await search_service.search(query="beethoven")

        assert result["results"] == []
        assert result["total"] == 0
        assert result["max_score"] is None
        assert "error" in result
        assert "Connection error" in result["error"]


class TestDeleteOperations:
    """Test delete operations."""

    @pytest.mark.asyncio
    async def test_delete_work(self, search_service, mock_es_client):
        """Test deleting a work from the index."""
        search_service.es = mock_es_client

        await search_service.delete_work(1)

        mock_es_client.delete.assert_called_once_with(
            index="musical_works",
            id=1
        )

    @pytest.mark.asyncio
    async def test_delete_work_not_found(self, search_service, mock_es_client):
        """Test deleting non-existent work (should not raise error)."""
        search_service.es = mock_es_client

        # Create proper NotFoundError with required parameters
        error = NotFoundError(
            message="document_not_found_exception",
            meta=MagicMock(),
            body={}
        )
        mock_es_client.delete.side_effect = error

        # Should not raise an error
        await search_service.delete_work(999)

        mock_es_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_work_error_handling(self, search_service, mock_es_client):
        """Test delete work error handling."""
        search_service.es = mock_es_client
        mock_es_client.delete.side_effect = Exception("Connection error")

        # Should not raise an error
        await search_service.delete_work(1)


class TestReindexing:
    """Test reindexing operations."""

    @pytest.mark.asyncio
    async def test_reindex_all_deletes_old_index(self, search_service, mock_es_client):
        """Test that reindex_all deletes the old index."""
        search_service.es = mock_es_client

        works = [
            {"id": 1, "title": "Work 1", "contributors": "Artist 1"},
            {"id": 2, "title": "Work 2", "contributors": "Artist 2"},
        ]

        await search_service.reindex_all(works)

        mock_es_client.indices.delete.assert_called_once_with(
            index="musical_works",
            ignore=[404]
        )

    @pytest.mark.asyncio
    async def test_reindex_all_creates_new_index(self, search_service, mock_es_client):
        """Test that reindex_all creates a new index."""
        search_service.es = mock_es_client

        with patch.object(search_service, "create_index") as mock_create:
            with patch.object(search_service, "bulk_index_works") as mock_bulk:
                mock_create.return_value = AsyncMock()
                mock_bulk.return_value = AsyncMock()

                works = [{"id": 1, "title": "Work 1"}]
                await search_service.reindex_all(works)

                mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_reindex_all_bulk_indexes(self, search_service, mock_es_client):
        """Test that reindex_all bulk indexes all works."""
        search_service.es = mock_es_client

        with patch.object(search_service, "create_index") as mock_create:
            with patch.object(search_service, "bulk_index_works") as mock_bulk:
                mock_create.return_value = AsyncMock()
                mock_bulk.return_value = AsyncMock()

                works = [
                    {"id": 1, "title": "Work 1"},
                    {"id": 2, "title": "Work 2"},
                    {"id": 3, "title": "Work 3"},
                ]

                await search_service.reindex_all(works)

                mock_bulk.assert_called_once_with(works)

    @pytest.mark.asyncio
    async def test_reindex_all_error_handling(self, search_service, mock_es_client):
        """Test reindex_all error handling."""
        search_service.es = mock_es_client
        mock_es_client.indices.delete.side_effect = Exception("Delete error")

        # Should not raise an error
        works = [{"id": 1, "title": "Work 1"}]
        await search_service.reindex_all(works)


class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    @pytest.mark.asyncio
    async def test_typical_search_workflow(self, search_service):
        """Test a typical search workflow: connect → create index → search."""
        with patch("app.services.search_service.AsyncElasticsearch") as mock_es_class:
            mock_es = AsyncMock()
            mock_es_class.return_value = mock_es

            # Setup mocks
            mock_es.indices = AsyncMock()
            mock_es.indices.exists = AsyncMock(return_value=False)
            mock_es.indices.create = AsyncMock()
            mock_es.search = AsyncMock(return_value={
                "hits": {
                    "hits": [{"_source": {"id": 1, "title": "Test"}, "_score": 1.0}],
                    "total": {"value": 1},
                    "max_score": 1.0
                }
            })

            # Connect
            await search_service.connect()
            assert search_service.es is not None

            # Create index
            await search_service.create_index()
            mock_es.indices.create.assert_called_once()

            # Search
            result = await search_service.search(query="test")
            assert result["total"] == 1
            assert len(result["results"]) == 1
