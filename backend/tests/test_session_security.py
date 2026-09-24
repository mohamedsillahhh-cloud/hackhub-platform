from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import create_action_token
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_refresh_tokens_rotate_and_reuse_revokes_session(db_session, test_user):
    service = AuthService(db_session)
    initial = await service.login(test_user.email, "testpass123")
    rotated = await service.refresh_token(initial["refresh_token"])

    with pytest.raises(HTTPException) as error:
        await service.refresh_token(initial["refresh_token"])

    assert error.value.status_code == 401
    with pytest.raises(HTTPException) as revoked_error:
        await service.refresh_token(rotated["refresh_token"])
    assert revoked_error.value.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_access_session(client, db_session, test_user):
    service = AuthService(db_session)
    tokens = await service.login(test_user.email, "testpass123")

    before = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert before.status_code == 200

    await service.logout(tokens["refresh_token"])
    after = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert after.status_code == 401


@pytest.mark.asyncio
async def test_password_reset_token_cannot_be_reused(db_session, test_user):
    token = create_action_token(
        {"sub": str(test_user.id), "version": test_user.password_reset_version},
        action="password_reset",
        expires_delta=timedelta(minutes=5),
    )
    service = AuthService(db_session)

    await service.confirm_password_reset(token, "new-password-123")
    with pytest.raises(HTTPException) as error:
        await service.confirm_password_reset(token, "another-password-123")

    assert error.value.status_code == 400
