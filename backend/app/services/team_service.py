from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team, TeamMember, MemberRole, InviteStatus
from app.models.event import Event
from app.models.notification import NotificationType, NotificationCategory
from app.repositories.team_repository import TeamRepository
from app.repositories.event_repository import EventRepository
from app.schemas.team import TeamCreate
from app.utils.helpers import generate_unique_code


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.team_repo = TeamRepository(db)
        self.event_repo = EventRepository(db)

    async def create_team(self, event_id: UUID, team_data: TeamCreate, leader_id: UUID) -> Team:
        event = await self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        teams = await self.team_repo.get_user_teams(leader_id)
            teams = await self.team_repo.get_user_teams(leader_id)
            for t in teams:
                if str(t.event_id) == str(event_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You already have a team in this event",
                    )

        invite_code = generate_unique_code()
        while await self.team_repo.get_by_invite_code(invite_code):
            invite_code = generate_unique_code()

        team = await self.team_repo.create(
            name=team_data.name,
            description=team_data.description,
            event_id=event_id,
            leader_id=leader_id,
            invitation_code=invite_code,
        )

        await self.team_repo.add_member(
            team_id=team.id,
            user_id=leader_id,
            role=MemberRole.LEADER,
            status=InviteStatus.ACCEPTED,
        )

        return await self.team_repo.get_team_with_members(team.id)

    async def invite_member(self, team_id: UUID, invited_user_id: UUID, inviter_id: UUID) -> TeamMember:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        if team.leader_id != inviter_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only team leader can invite members")

        event = await self.event_repo.get(team.event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        accepted_count = sum(1 for m in team.members if m.status == InviteStatus.ACCEPTED)
        if accepted_count >= event.max_team_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team already has maximum {event.max_team_size} members",
            )

        existing_member = await self.team_repo.get_member(team_id, invited_user_id)
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already invited or is a member of this team",
            )

        member = await self.team_repo.add_member(
            team_id=team_id,
            user_id=invited_user_id,
            role=MemberRole.MEMBER,
            status=InviteStatus.PENDING,
            invited_by=inviter_id,
        )

        from app.services.notification_service import NotificationService
        notif_service = NotificationService(self.db)
        await notif_service.send_notification(
            user_id=invited_user_id,
            notification_type=NotificationType.PUSH,
            category=NotificationCategory.TEAM_INVITE,
            title=f"Team Invitation: {team.name}",
            message=f"You have been invited to join team '{team.name}'",
            data={"team_id": str(team.id), "event_id": str(team.event_id)},
        )

        return member

    async def accept_invite(self, team_id: UUID, member_id: UUID, user_id: UUID) -> TeamMember:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        member = None
        for m in team.members:
            if str(m.id) == str(member_id):
                member = m
                break
        if not member or str(member.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        if member.status != InviteStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite already processed")

        member.status = InviteStatus.ACCEPTED
        await self.db.flush()
        return member

    async def reject_invite(self, team_id: UUID, member_id: UUID, user_id: UUID) -> TeamMember:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        member = None
        for m in team.members:
            if str(m.id) == str(member_id):
                member = m
                break
        if not member or str(member.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        if member.status != InviteStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite already processed")

        member.status = InviteStatus.REJECTED
        await self.db.flush()
        return member

    async def leave_team(self, team_id: UUID, user_id: UUID) -> None:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

        if team.leader_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team leader cannot leave. Transfer leadership first or delete the team.",
            )

        member = await self.team_repo.get_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        await self.team_repo.remove_member(member.id)

    async def remove_member(self, team_id: UUID, member_id: UUID, user_id: UUID) -> None:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        if team.leader_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only team leader can remove members")

        member = None
        for m in team.members:
            if str(m.id) == str(member_id):
                member = m
                break
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        if member.user_id == team.leader_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove team leader")

        await self.team_repo.remove_member(member.id)

    async def change_leader(self, team_id: UUID, new_leader_id: UUID, current_user_id: UUID) -> Team:
        team = await self.team_repo.get_team_with_members(team_id)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        if team.leader_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leader can transfer leadership")

        member = await self.team_repo.get_member(team_id, new_leader_id)
        if not member or member.status != InviteStatus.ACCEPTED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not an active member of the team")

        old_leader_member = await self.team_repo.get_member(team_id, current_user_id)
        if old_leader_member:
            old_leader_member.role = MemberRole.MEMBER
        member.role = MemberRole.LEADER
        team.leader_id = new_leader_id
        await self.db.flush()
        return team

    async def get_team_by_invite_code(self, code: str) -> Team:
        team = await self.team_repo.get_by_invite_code(code)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team

    async def join_by_code(self, code: str, user_id: UUID) -> TeamMember:
        team = await self.team_repo.get_by_invite_code(code)
        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invitation code")

        event = await self.event_repo.get(team.event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        accepted_count = sum(1 for m in team.members if m.status == InviteStatus.ACCEPTED)
        if accepted_count >= event.max_team_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team already has maximum {event.max_team_size} members",
            )

        existing = await self.team_repo.get_member(team.id, user_id)
        if existing:
            if existing.status == InviteStatus.ACCEPTED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member of this team")
            existing.status = InviteStatus.ACCEPTED
            return existing

        member = await self.team_repo.add_member(
            team_id=team.id,
            user_id=user_id,
            role=MemberRole.MEMBER,
            status=InviteStatus.ACCEPTED,
        )
        return member

    async def list_event_teams(self, event_id: UUID) -> List[Team]:
        return await self.team_repo.get_by_event(event_id)
