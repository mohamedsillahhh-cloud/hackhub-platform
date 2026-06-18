import pytest


class TestAuthIntegration:
    @pytest.mark.asyncio
    async def test_register_success(self, async_client):
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "SecurePass123!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client):
        await async_client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "username": "user1",
            "full_name": "User 1",
            "password": "SecurePass123!",
        })
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "username": "user2",
            "full_name": "User 2",
            "password": "SecurePass123!",
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, async_client):
        await async_client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "full_name": "Login User",
            "password": "SecurePass123!",
        })
        response = await async_client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123!",
        })
        assert response.status_code == 200
        assert "access_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client):
        await async_client.post("/api/v1/auth/register", json={
            "email": "wrong@example.com",
            "username": "wronguser",
            "full_name": "Wrong User",
            "password": "SecurePass123!",
        })
        response = await async_client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com",
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_clears_cookies(self, async_client):
        await async_client.post("/api/v1/auth/register", json={
            "email": "logout@example.com",
            "username": "logoutuser",
            "full_name": "Logout User",
            "password": "SecurePass123!",
        })
        login_resp = await async_client.post("/api/v1/auth/login", json={
            "email": "logout@example.com",
            "password": "SecurePass123!",
        })
        cookies = login_resp.cookies
        logout_resp = await async_client.post("/api/v1/auth/logout", cookies=cookies)
        assert logout_resp.status_code == 200
        assert logout_resp.cookies.get("access_token") is None or logout_resp.cookies["access_token"] == ""
