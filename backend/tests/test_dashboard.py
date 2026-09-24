from datetime import datetime, timedelta, timezone

import pytest

from app.models.event import Event, EventStatus


@pytest.mark.asyncio
async def test_public_dashboard_stats_need_no_auth_and_hide_drafts(client, db_session, admin_user):
    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            Event(
                title="Visible event",
                start_date=now + timedelta(days=1),
                end_date=now + timedelta(days=2),
                organizer_id=admin_user.id,
                status=EventStatus.PUBLISHED,
            ),
            Event(
                title="Private draft",
                start_date=now + timedelta(days=3),
                end_date=now + timedelta(days=4),
                organizer_id=admin_user.id,
                status=EventStatus.DRAFT,
            ),
        ]
    )
    await db_session.flush()

    response = await client.get("/api/v1/dashboard/public-stats")

    assert response.status_code == 200
    assert response.json()["total_events"] == 1


@pytest.mark.asyncio
async def test_participant_cannot_access_management_dashboard(client, auth_headers):
    response = await client.get("/api/v1/dashboard/stats", headers=auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_organizer_dashboard_is_scoped_to_owned_events(
    client,
    db_session,
    organizer_user,
    organizer_headers,
    admin_user,
):
    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            Event(
                title="Organizer event",
                start_date=now + timedelta(days=1),
                end_date=now + timedelta(days=2),
                organizer_id=organizer_user.id,
            ),
            Event(
                title="Another organizer event",
                start_date=now + timedelta(days=3),
                end_date=now + timedelta(days=4),
                organizer_id=admin_user.id,
            ),
        ]
    )
    await db_session.flush()

    response = await client.get("/api/v1/dashboard/stats", headers=organizer_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_events"] == 1
    assert [event["title"] for event in payload["recent_events"]] == ["Organizer event"]


@pytest.mark.asyncio
async def test_admin_dashboard_remains_global(client, db_session, admin_user, admin_headers, organizer_user):
    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            Event(
                title="Admin event",
                start_date=now + timedelta(days=1),
                end_date=now + timedelta(days=2),
                organizer_id=admin_user.id,
            ),
            Event(
                title="Organizer event",
                start_date=now + timedelta(days=3),
                end_date=now + timedelta(days=4),
                organizer_id=organizer_user.id,
            ),
        ]
    )
    await db_session.flush()

    response = await client.get("/api/v1/dashboard/stats", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["total_events"] == 2


@pytest.mark.asyncio
async def test_managed_events_are_scoped_to_organizer(
    client,
    db_session,
    organizer_user,
    organizer_headers,
    admin_user,
):
    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            Event(
                title="Owned event",
                start_date=now + timedelta(days=1),
                end_date=now + timedelta(days=2),
                organizer_id=organizer_user.id,
            ),
            Event(
                title="Foreign event",
                start_date=now + timedelta(days=3),
                end_date=now + timedelta(days=4),
                organizer_id=admin_user.id,
            ),
        ]
    )
    await db_session.flush()

    response = await client.get("/api/v1/events/managed", headers=organizer_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Owned event"


@pytest.mark.asyncio
async def test_participant_cannot_list_managed_events(client, auth_headers):
    response = await client.get("/api/v1/events/managed", headers=auth_headers)

    assert response.status_code == 403
