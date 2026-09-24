from datetime import datetime, timedelta, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.rate_limit import limiter
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.auth_session import AuthSession
from app.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session):
    limiter.reset()

    async def override_get_db():
        yield db_session

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(async_client):
    yield async_client


async def _create_user(db_session, *, role: UserRole, suffix: str) -> User:
    user = User(
        email=f"{suffix}@example.com",
        username=suffix,
        hashed_password=get_password_hash("testpass123"),
        full_name=f"{suffix.title()} User",
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_user(db_session):
    return await _create_user(db_session, role=UserRole.PARTICIPANT, suffix="participant")


@pytest_asyncio.fixture
async def second_user(db_session):
    return await _create_user(db_session, role=UserRole.PARTICIPANT, suffix="participant2")


@pytest_asyncio.fixture
async def admin_user(db_session):
    return await _create_user(db_session, role=UserRole.ADMIN, suffix="admin")


@pytest_asyncio.fixture
async def organizer_user(db_session):
    return await _create_user(db_session, role=UserRole.ORGANIZER, suffix="organizer")


@pytest_asyncio.fixture
async def judge_user(db_session):
    return await _create_user(db_session, role=UserRole.JUDGE, suffix="judge")


async def _auth_headers(db_session, user: User) -> dict:
    session = AuthSession(
        user_id=user.id,
        refresh_token_hash="fixture",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    db_session.add(session)
    await db_session.flush()
    token = create_access_token({"sub": str(user.id), "sid": str(session.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers(db_session, test_user):
    return await _auth_headers(db_session, test_user)


@pytest_asyncio.fixture
async def second_user_headers(db_session, second_user):
    return await _auth_headers(db_session, second_user)


@pytest_asyncio.fixture
async def admin_headers(db_session, admin_user):
    return await _auth_headers(db_session, admin_user)


@pytest_asyncio.fixture
async def organizer_headers(db_session, organizer_user):
    return await _auth_headers(db_session, organizer_user)


@pytest_asyncio.fixture
async def judge_headers(db_session, judge_user):
    return await _auth_headers(db_session, judge_user)
