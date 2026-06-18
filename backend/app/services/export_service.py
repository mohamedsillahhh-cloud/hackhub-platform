import csv
import io
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.evaluation import Evaluation, EvaluationScore
from app.models.user import User, UserRole


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _check_event_access(self, event_id: UUID, user: User) -> Event:
        result = await self.db.execute(select(Event).where(Event.id == event_id))
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        if user.role not in (UserRole.ADMIN, UserRole.ORGANIZER) and str(event.organizer_id) != str(user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return event

    async def export_participants(self, event_id: UUID, user: User, fmt: str = "xlsx"):
        await self._check_event_access(event_id, user)
        result = await self.db.execute(
            select(User, TeamMember, Team)
            .join(TeamMember, User.id == TeamMember.user_id)
            .join(Team, TeamMember.team_id == Team.id)
            .where(Team.event_id == event_id)
        )
        rows = result.all()
        headers = ["Name", "Email", "University", "Team", "Role", "Registered At"]
        data = [[r.User.full_name, r.User.email, r.User.university or "",
                 r.Team.name, r.TeamMember.role.value, str(r.TeamMember.created_at)] for r in rows]
        return self._stream_response(headers, data, fmt, "participants")

    async def export_projects(self, event_id: UUID, user: User, fmt: str = "xlsx"):
        await self._check_event_access(event_id, user)
        result = await self.db.execute(
            select(Project).where(Project.event_id == event_id)
        )
        projects = result.scalars().all()
        headers = ["Name", "Description", "Team ID", "Tech Stack", "Status", "Submitted At"]
        data = [[p.name, p.description or "", str(p.team_id),
                 ", ".join(p.tech_stack) if p.tech_stack else "", p.status.value,
                 str(p.submitted_at or "")] for p in projects]
        return self._stream_response(headers, data, fmt, "projects")

    async def export_ranking(self, event_id: UUID, user: User, fmt: str = "xlsx"):
        await self._check_event_access(event_id, user)
        from app.services.ranking_service import RankingService
        svc = RankingService(self.db)
        entries = await svc.get_ranking(event_id)
        headers = ["Position", "Team", "Project", "Total Score"]
        data = [[e["position"], e.get("team_name", ""), e.get("project_name", ""), e.get("total_score", 0)] for e in entries]
        return self._stream_response(headers, data, fmt, "ranking")

    async def export_evaluations(self, event_id: UUID, user: User, fmt: str = "xlsx"):
        await self._check_event_access(event_id, user)
        result = await self.db.execute(
            select(Evaluation, EvaluationScore)
            .join(EvaluationScore, Evaluation.id == EvaluationScore.evaluation_id)
            .where(Evaluation.project_id.in_(
                select(Project.id).where(Project.event_id == event_id)
            ))
        )
        rows = result.all()
        headers = ["Evaluation ID", "Project ID", "Judge ID", "Criterion ID", "Score", "Comment", "Submitted At"]
        data = [[str(r.Evaluation.id), str(r.Evaluation.project_id), str(r.Evaluation.judge_id),
                 str(r.EvaluationScore.criterion_id), r.EvaluationScore.score,
                 r.Evaluation.comment or "", str(r.Evaluation.submitted_at)] for r in rows]
        return self._stream_response(headers, data, fmt, "evaluations")

    def _stream_response(self, headers: List[str], data: List[List], fmt: str, filename: str):
        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(headers)
            writer.writerows(data)
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
            )
        else:
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = filename
                ws.append(headers)
                for row in data:
                    ws.append(row)
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                return StreamingResponse(
                    output,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
                )
            except Exception:
                raise HTTPException(status_code=500, detail="Excel export failed. Install openpyxl: pip install openpyxl")
