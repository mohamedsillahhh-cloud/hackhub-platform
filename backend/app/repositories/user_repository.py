from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get(self, id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).options(noload("*")).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).options(noload("*")).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).options(noload("*")).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> List[User]:
        result = await self.db.execute(select(User).options(noload("*")).where(User.role == role))
        return list(result.scalars().all())

    async def search_by_skills(
        self,
        skills: List[str],
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[User], int]:
        filters = []
        for skill in skills:
            filters.append(cast(User.skills, String).like(f'%"{skill}"%'))
        query = select(User).options(noload("*")).where(or_(*filters))
        count_query = select(func.count(User.id)).where(or_(*filters))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        total_users = await self.db.execute(select(func.count(User.id)))
        active_participants = await self.db.execute(
            select(func.count(User.id)).where(User.role == UserRole.PARTICIPANT, User.is_active.is_(True))
        )
        universities = await self.db.execute(
            select(func.count(func.distinct(User.university))).where(User.university.isnot(None))
        )
        countries = await self.db.execute(
            select(func.count(func.distinct(User.country))).where(User.country.isnot(None))
        )

        return {
            "total_users": total_users.scalar() or 0,
            "active_participants": active_participants.scalar() or 0,
            "universities": universities.scalar() or 0,
            "countries": countries.scalar() or 0,
        }

    async def list_users_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        skills: Optional[List[str]] = None,
        university: Optional[str] = None,
        country: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        query = select(User).options(noload("*"))
        count_query = select(func.count(User.id))

        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        if university:
            query = query.where(User.university.ilike(f"%{university}%"))
            count_query = count_query.where(User.university.ilike(f"%{university}%"))
        if country:
            query = query.where(User.country.ilike(f"%{country}%"))
            count_query = count_query.where(User.country.ilike(f"%{country}%"))
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        if skills:
            skill_filters = [cast(User.skills, String).like(f'%"{skill}"%') for skill in skills]
            query = query.where(or_(*skill_filters))
            count_query = count_query.where(or_(*skill_filters))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
