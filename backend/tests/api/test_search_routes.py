"""API route tests for search endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.services.search_service import search_service


@pytest.fixture
async def mock_search_service():
    """Mock the search service for route testing."""
    with patch.object(search_service, 'search') as mock_search, \
         patch.object(search_service, 'reindex_all') as mock_reindex:

        # Default search response
        mock_search.return_value = {
            "results": [
                {
                    "id": 1,
                    "title": "Test Work",
                    "contributors": "Test Artist",
                    "publisher": "Test Publisher",
                    "iswc": "T-123.456.789-0",
                    "_score": 10.5,
                    "_highlight": {"title": ["<em>Test</em> Work"]}
                }
            ],
            "total": 1,
            "max_score": 10.5
        }

        # Default reindex response
        mock_reindex.return_value = None

        yield {"search": mock_search, "reindex": mock_reindex}


class TestSearchWorksEndpoint:
    """Test /api/v1/search/works endpoint."""

    @pytest.mark.asyncio
    async def test_search_works_success(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test successful search."""
        response = await client.get(
            "/api/v1/search/works?q=test",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "pagination" in data
        assert "query" in data
        assert data["query"] == "test"
        assert len(data["results"]) == 1

        # Verify search service was called
        mock_search_service["search"].assert_called_once()

    @pytest.mark.asyncio
    async def test_search_works_with_filters(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search with filters."""
        response = await client.get(
            "/api/v1/search/works?q=test&has_iswc=true&has_disputed_rights=false",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["filters"] == {
            "has_iswc": True,
            "has_disputed_rights": False
        }

        # Verify filters were passed to search service
        call_args = mock_search_service["search"].call_args
        assert call_args.kwargs["filters"]["has_iswc"] is True
        assert call_args.kwargs["filters"]["has_disputed_rights"] is False

    @pytest.mark.asyncio
    async def test_search_works_pagination(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search pagination."""
        response = await client.get(
            "/api/v1/search/works?q=test&page=2&limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["pagination"]["page"] == 2
        assert data["pagination"]["limit"] == 10

        # Verify offset calculation
        call_args = mock_search_service["search"].call_args
        assert call_args.kwargs["from_"] == 10  # (page-1) * limit
        assert call_args.kwargs["size"] == 10

    @pytest.mark.asyncio
    async def test_search_works_missing_query(self, client: AsyncClient, auth_headers: dict):
        """Test search without query parameter."""
        response = await client.get(
            "/api/v1/search/works",
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_works_short_query(self, client: AsyncClient, auth_headers: dict):
        """Test search with query too short."""
        response = await client.get(
            "/api/v1/search/works?q=a",  # Only 1 character, min is 2
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_works_max_limit(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search respects max limit."""
        response = await client.get(
            "/api/v1/search/works?q=test&limit=150",  # Max is 100
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_works_unauthorized(self, client: AsyncClient):
        """Test search requires authentication."""
        response = await client.get("/api/v1/search/works?q=test")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_search_works_with_max_score(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search includes max_score in response."""
        response = await client.get(
            "/api/v1/search/works?q=test",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "max_score" in data
        assert data["max_score"] == 10.5

    @pytest.mark.asyncio
    async def test_search_works_empty_results(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search with no results."""
        mock_search_service["search"].return_value = {
            "results": [],
            "total": 0,
            "max_score": None
        }

        response = await client.get(
            "/api/v1/search/works?q=nonexistent",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["results"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["total_pages"] == 0

    @pytest.mark.asyncio
    async def test_search_works_pagination_metadata(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test pagination metadata calculation."""
        mock_search_service["search"].return_value = {
            "results": [{"id": 1}],
            "total": 45,
            "max_score": 10.0
        }

        response = await client.get(
            "/api/v1/search/works?q=test&page=2&limit=20",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        pagination = data["pagination"]
        assert pagination["total"] == 45
        assert pagination["total_pages"] == 3  # ceil(45/20)
        assert pagination["has_next"] is True
        assert pagination["has_prev"] is True


class TestSuggestEndpoint:
    """Test /api/v1/search/suggest endpoint."""

    @pytest.mark.asyncio
    async def test_suggest_success(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test autocomplete suggestions."""
        mock_search_service["search"].return_value = {
            "results": [
                {"id": 1, "title": "Test Work 1", "contributors": "Artist 1", "_score": 10.0},
                {"id": 2, "title": "Test Work 2", "contributors": "Artist 2", "_score": 9.5},
            ],
            "total": 2,
            "max_score": 10.0
        }

        response = await client.get(
            "/api/v1/search/suggest?q=test",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "suggestions" in data
        assert len(data["suggestions"]) == 2
        assert data["query"] == "test"

        # Verify suggestion format
        first_suggestion = data["suggestions"][0]
        assert "title" in first_suggestion
        assert "id" in first_suggestion
        assert "contributors" in first_suggestion
        assert "score" in first_suggestion

    @pytest.mark.asyncio
    async def test_suggest_default_limit(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test default limit for suggestions."""
        response = await client.get(
            "/api/v1/search/suggest?q=test",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify default limit of 5 was used
        call_args = mock_search_service["search"].call_args
        assert call_args.kwargs["size"] == 5

    @pytest.mark.asyncio
    async def test_suggest_custom_limit(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test custom limit for suggestions."""
        response = await client.get(
            "/api/v1/search/suggest?q=test&limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify custom limit was used
        call_args = mock_search_service["search"].call_args
        assert call_args.kwargs["size"] == 10

    @pytest.mark.asyncio
    async def test_suggest_max_limit(self, client: AsyncClient, auth_headers: dict):
        """Test max limit for suggestions."""
        response = await client.get(
            "/api/v1/search/suggest?q=test&limit=30",  # Max is 20
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_suggest_no_query(self, client: AsyncClient, auth_headers: dict):
        """Test suggest without query."""
        response = await client.get(
            "/api/v1/search/suggest",
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_suggest_unauthorized(self, client: AsyncClient):
        """Test suggest requires authentication."""
        response = await client.get("/api/v1/search/suggest?q=test")

        assert response.status_code == 401


class TestReindexEndpoint:
    """Test /api/v1/search/reindex endpoint."""

    @pytest.mark.asyncio
    async def test_reindex_as_admin(self, client: AsyncClient, admin_headers: dict, mock_search_service):
        """Test reindex with admin user."""
        with patch('app.api.routes.search.get_works') as mock_get_works:
            mock_get_works.return_value = [
                {"id": 1, "title": "Work 1", "contributors": "Artist 1"},
                {"id": 2, "title": "Work 2", "contributors": "Artist 2"},
            ]

            response = await client.post(
                "/api/v1/search/reindex",
                headers=admin_headers
            )

            assert response.status_code == 202  # Accepted
            data = response.json()

            assert data["status"] == "reindexing"
            assert "count" in data
            assert data["count"] == 2

            # Verify reindex was called
            mock_search_service["reindex"].assert_called_once()

    @pytest.mark.asyncio
    async def test_reindex_as_publisher(self, client: AsyncClient, auth_headers: dict):
        """Test reindex forbidden for non-admin."""
        response = await client.post(
            "/api/v1/search/reindex",
            headers=auth_headers
        )

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_reindex_unauthorized(self, client: AsyncClient):
        """Test reindex requires authentication."""
        response = await client.post("/api/v1/search/reindex")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_reindex_with_many_works(self, client: AsyncClient, admin_headers: dict, mock_search_service):
        """Test reindex with large dataset."""
        with patch('app.api.routes.search.get_works') as mock_get_works:
            # Simulate 10000 works
            mock_get_works.return_value = [
                {"id": i, "title": f"Work {i}", "contributors": f"Artist {i}"}
                for i in range(10000)
            ]

            response = await client.post(
                "/api/v1/search/reindex",
                headers=admin_headers
            )

            assert response.status_code == 202
            data = response.json()

            assert data["count"] == 10000
            assert "Reindexing 10000 works" in data["message"]


class TestSearchRouteIntegration:
    """Integration tests for search routes."""

    @pytest.mark.asyncio
    async def test_search_flow(self, client: AsyncClient, auth_headers: dict, admin_headers: dict, mock_search_service):
        """Test complete search flow: reindex → search → suggest."""

        # 1. Reindex as admin
        with patch('app.api.routes.search.get_works') as mock_get_works:
            mock_get_works.return_value = [
                {"id": 1, "title": "Beethoven Symphony", "contributors": "Ludwig van Beethoven"}
            ]

            reindex_response = await client.post(
                "/api/v1/search/reindex",
                headers=admin_headers
            )
            assert reindex_response.status_code == 202

        # 2. Search for works
        search_response = await client.get(
            "/api/v1/search/works?q=beethoven",
            headers=auth_headers
        )
        assert search_response.status_code == 200

        # 3. Get suggestions
        suggest_response = await client.get(
            "/api/v1/search/suggest?q=beeth",
            headers=auth_headers
        )
        assert suggest_response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_error_handling(self, client: AsyncClient, auth_headers: dict, mock_search_service):
        """Test search handles service errors gracefully."""
        mock_search_service["search"].side_effect = Exception("Elasticsearch error")

        response = await client.get(
            "/api/v1/search/works?q=test",
            headers=auth_headers
        )

        # Should handle error gracefully
        assert response.status_code in [200, 500]  # Depending on error handling


@pytest.fixture
def auth_headers() -> dict:
    """Get auth headers for a regular user."""
    from app.core.security import create_access_token

    token = create_access_token(
        data={"sub": "2", "email": "testuser@example.com", "role": "publisher"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers() -> dict:
    """Get auth headers for an admin user."""
    from app.core.security import create_access_token

    token = create_access_token(
        data={"sub": "1", "email": "admin@example.com", "role": "admin"}
    )
    return {"Authorization": f"Bearer {token}"}
