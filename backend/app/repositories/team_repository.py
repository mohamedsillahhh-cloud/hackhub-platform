from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.team import Team, TeamMember
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db: AsyncSession):
        super().__init__(Team, db)

    async def get_by_event(self, event_id: UUID) -> List[Team]:
        result = await self.db.execute(
            select(Team)
            .where(Team.event_id == event_id)
            .options(joinedload(Team.members))
            .order_by(Team.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def get_by_invite_code(self, code: str) -> Optional[Team]:
        result = await self.db.execute(
            select(Team).where(Team.invitation_code == code).options(joinedload(Team.members))
        )
        return result.unique().scalar_one_or_none()

    async def get_user_teams(self, user_id: UUID) -> List[Team]:
        result = await self.db.execute(
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == user_id)
            .options(joinedload(Team.members))
            .order_by(Team.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def get_team_with_members(self, team_id: UUID) -> Optional[Team]:
        result = await self.db.execute(
            select(Team).where(Team.id == team_id).options(joinedload(Team.members))
        )
        return result.unique().scalar_one_or_none()

    async def get_member(self, team_id: UUID, user_id: UUID) -> Optional[TeamMember]:
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_member(self, **kwargs) -> TeamMember:
        member = TeamMember(**kwargs)
        self.db.add(member)
        await self.db.flush()
        return member

    async def remove_member(self, member_id: UUID) -> bool:
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.id == member_id)
        )
        member = result.scalar_one_or_none()
        if not member:
            return False
        await self.db.delete(member)
        await self.db.flush()
        return True

    async def get_team_members(self, team_id: UUID) -> List[TeamMember]:
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        )
        return list(result.scalars().all())

    async def get_members_count(self, team_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(TeamMember.id)).where(
                TeamMember.team_id == team_id,
                TeamMember.status == "accepted",
            )
        )
        return result.scalar() or 0
