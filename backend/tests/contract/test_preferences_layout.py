"""Contract test for POST /api/v1/preferences/layout endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_dashboard_layout_valid_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test dashboard layout update with valid configuration."""
    request_payload = {
        "layout": {
            "widgets": [
                {"id": "stats-overview", "x": 0, "y": 0, "w": 12, "h": 2},
                {"id": "activity-feed", "x": 0, "y": 2, "w": 6, "h": 4},
                {"id": "charts-panel", "x": 6, "y": 2, "w": 6, "h": 4},
            ]
        }
    }

    response = await client.post(
        "/api/v1/preferences/layout", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "dashboard_layout" in data
    assert "widgets" in data["dashboard_layout"]
    assert len(data["dashboard_layout"]["widgets"]) == 3


@pytest.mark.asyncio
async def test_update_layout_invalid_widget_schema_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test layout update with invalid widget schema."""
    request_payload = {
        "layout": {
            "widgets": [
                {"id": "invalid-widget", "x": "not-a-number", "y": 0}  # Missing w, h
            ]
        }
    }

    response = await client.post(
        "/api/v1/preferences/layout", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_layout_missing_required_fields_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test layout update without required layout field."""
    request_payload = {}  # Missing 'layout' field

    response = await client.post(
        "/api/v1/preferences/layout", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 422
