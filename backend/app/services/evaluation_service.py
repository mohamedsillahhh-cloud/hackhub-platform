from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation, EvaluationScore
from app.models.project import Project, ProjectStatus
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.event_repository import EventRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.evaluation import EvaluationCreate, RankResponse


class EvaluationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.eval_repo = EvaluationRepository(db)
        self.project_repo = ProjectRepository(db)
        self.event_repo = EventRepository(db)
        self.team_repo = TeamRepository(db)

    async def submit_evaluation(self, event_id: UUID, eval_data: EvaluationCreate, judge_id: UUID) -> Evaluation:
        project = await self.project_repo.get(UUID(eval_data.project_id))
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if str(project.event_id) != str(event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not belong to this event",
            )
        if project.status not in (ProjectStatus.SUBMITTED, ProjectStatus.FINALIZED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot evaluate a non-submitted project",
            )

        existing = await self.eval_repo.get_evaluation_for_project_and_judge(
            UUID(eval_data.project_id), judge_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already evaluated this project",
            )

        total_score = 0.0
        scores_data = []

        for score_item in eval_data.scores:
            from app.models.challenge import Criterion
            result = await self.db.execute(
                __import__("sqlalchemy").select(Criterion).where(Criterion.id == UUID(score_item.criterion_id))
            )
            criterion = result.scalar_one_or_none()
            if not criterion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Criterion {score_item.criterion_id} not found",
                )
            weighted = score_item.score * criterion.weight
            total_score += weighted
            scores_data.append({
                "criterion_id": UUID(score_item.criterion_id),
                "score": score_item.score,
            })

        evaluation = await self.eval_repo.create(
            project_id=UUID(eval_data.project_id),
            judge_id=judge_id,
            comment=eval_data.comment,
            total_score=total_score,
        )

        for s in scores_data:
            score = EvaluationScore(
                evaluation_id=evaluation.id,
                criterion_id=s["criterion_id"],
                score=s["score"],
            )
            self.db.add(score)

        await self.db.flush()
        await self.db.refresh(evaluation)
        return evaluation

    async def get_project_evaluations(self, project_id: UUID) -> List[Evaluation]:
        return await self.eval_repo.get_by_project(project_id)

    async def get_ranking(self, event_id: UUID) -> List[RankResponse]:
        rows = await self.eval_repo.get_ranking_data(event_id)
        rankings = []
        for position, row in enumerate(rows, start=1):
            rankings.append(
                RankResponse(
                    position=position,
                    project_id=str(row.project_id),
                    project_name=row.project_name,
                    team_id=str(row.team_id),
                    team_name=row.team_name,
                    total_score=float(row.total_score),
                    evaluation_count=row.evaluation_count,
                )
            )
        return rankings
