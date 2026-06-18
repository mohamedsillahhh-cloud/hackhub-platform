import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, admin_headers: dict):
    response = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Test Hackathon",
            "description": "A test event",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
            "location": "Online",
            "is_online": True,
            "max_team_size": 4,
            "min_team_size": 1,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Hackathon"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_create_event_unauthorized(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/events/",
        headers=auth_headers,
        json={
            "title": "Unauthorized Event",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_events(client: AsyncClient, admin_headers: dict):
    await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Event 1",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Event 2",
            "start_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=16)).isoformat(),
        },
    )

    response = await client.get("/api/v1/events/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_event(client: AsyncClient, admin_headers: dict):
    create_resp = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Specific Event",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    event_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Event"


@pytest.mark.asyncio
async def test_update_event(client: AsyncClient, admin_headers: dict):
    create_resp = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Update Me",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    event_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/events/{event_id}",
        headers=admin_headers,
        json={"title": "Updated Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_event(client: AsyncClient, admin_headers: dict):
    create_resp = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Delete Me",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    event_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/events/{event_id}", headers=admin_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_change_event_status(client: AsyncClient, admin_headers: dict):
    create_resp = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Status Test",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    event_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/events/{event_id}/status?new_status=published",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "published"


@pytest.mark.asyncio
async def test_change_event_status_invalid(client: AsyncClient, admin_headers: dict):
    create_resp = await client.post(
        "/api/v1/events/",
        headers=admin_headers,
        json={
            "title": "Invalid Status",
            "start_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=9)).isoformat(),
        },
    )
    event_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/events/{event_id}/status?new_status=closed",
        headers=admin_headers,
    )
    assert response.status_code == 400
