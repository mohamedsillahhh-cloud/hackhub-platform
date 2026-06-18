from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation, EvaluationScore
from app.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository[Evaluation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Evaluation, db)

    async def get_by_project(self, project_id: UUID) -> List[Evaluation]:
        result = await self.db.execute(
            select(Evaluation).where(Evaluation.project_id == project_id).order_by(Evaluation.submitted_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_judge(self, judge_id: UUID, event_id: Optional[UUID] = None) -> List[Evaluation]:
        query = select(Evaluation).where(Evaluation.judge_id == judge_id)
        if event_id:
            from app.models.project import Project
            query = query.join(Project).where(Project.event_id == event_id)
        query = query.order_by(Evaluation.submitted_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_average_scores(self, project_id: UUID) -> dict:
        result = await self.db.execute(
            select(
                func.avg(Evaluation.total_score).label("average"),
                func.count(Evaluation.id).label("count"),
            ).where(Evaluation.project_id == project_id)
        )
        row = result.one()
        return {"average": float(row.average) if row.average else 0.0, "count": row.count or 0}

    async def get_ranking_data(self, event_id: UUID) -> list:
        from app.models.project import Project
        from app.models.team import Team
        from sqlalchemy import desc

        result = await self.db.execute(
            select(
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                Project.team_id,
                Team.name.label("team_name"),
                func.coalesce(func.avg(Evaluation.total_score), 0).label("total_score"),
                func.count(Evaluation.id).label("evaluation_count"),
            )
            .select_from(Project)
            .join(Team, Project.team_id == Team.id)
            .outerjoin(Evaluation, Project.id == Evaluation.project_id)
            .where(Project.event_id == event_id, Project.status.in_(["submitted", "finalized"]))
            .group_by(Project.id, Project.name, Project.team_id, Team.name)
            .order_by(desc(func.coalesce(func.avg(Evaluation.total_score), 0)))
        )
        return list(result.all())

    async def get_evaluation_for_project_and_judge(self, project_id: UUID, judge_id: UUID) -> Optional[Evaluation]:
        result = await self.db.execute(
            select(Evaluation).where(
                and_(
                    Evaluation.project_id == project_id,
                    Evaluation.judge_id == judge_id,
                )
            )
        )
        return result.scalar_one_or_none()
