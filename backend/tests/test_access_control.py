from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import create_action_token, get_password_hash
from app.models.challenge import ChallengeCategory
from app.models.event import Event
from app.models.notification import Notification, NotificationCategory, NotificationType
from app.models.team import Team
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_email_action_token_cannot_authenticate(client, test_user):
    token = create_action_token(
        {"sub": str(test_user.id)},
        action="password_reset",
        expires_delta=timedelta(minutes=30),
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_mark_another_users_notification_as_read(client, db_session, auth_headers, test_user):
    other_user = User(
        email="other@example.com",
        username="other-user",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.PARTICIPANT,
    )
    db_session.add(other_user)
    await db_session.flush()
    notification = Notification(
        user_id=other_user.id,
        type=NotificationType.PUSH,
        category=NotificationCategory.TEAM_INVITE,
        title="Private notification",
        message="Only the owner may update this.",
    )
    db_session.add(notification)
    await db_session.flush()

    response = await client.put(f"/api/v1/notifications/{notification.id}/read", headers=auth_headers)

    assert response.status_code == 404
    assert notification.read is False


@pytest.mark.asyncio
async def test_nested_team_route_enforces_event_scope_and_hides_invite_code(client, db_session, admin_user):
    now = datetime.now(timezone.utc)
    first_event = Event(
        title="First event",
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        organizer_id=admin_user.id,
    )
    second_event = Event(
        title="Second event",
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=4),
        organizer_id=admin_user.id,
    )
    db_session.add_all([first_event, second_event])
    await db_session.flush()
    team = Team(
        name="Scoped team",
        event_id=first_event.id,
        leader_id=admin_user.id,
        invitation_code="PRIVATE1",
    )
    db_session.add(team)
    await db_session.flush()

    valid_response = await client.get(f"/api/v1/events/{first_event.id}/teams/{team.id}")
    wrong_event_response = await client.get(f"/api/v1/events/{second_event.id}/teams/{team.id}")

    assert valid_response.status_code == 200
    assert "invitation_code" not in valid_response.json()
    assert wrong_event_response.status_code == 404


@pytest.mark.asyncio
async def test_categories_static_route_is_not_shadowed_by_challenge_id(client, db_session, admin_user):
    now = datetime.now(timezone.utc)
    event = Event(
        title="Categories event",
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=2),
        organizer_id=admin_user.id,
    )
    db_session.add(event)
    await db_session.flush()
    db_session.add(ChallengeCategory(event_id=event.id, name="Main", order=1))
    await db_session.flush()

    response = await client.get(f"/api/v1/events/{event.id}/challenges/categories")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Main"
