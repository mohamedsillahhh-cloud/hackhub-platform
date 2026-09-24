from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.models.challenge import Challenge, ChallengeCategory, Criterion
from app.models.evaluation import Evaluation, EvaluationScore
from app.models.project import ProjectStatus
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.event_repository import EventRepository
from app.repositories.project_repository import ProjectRepository
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
        project = await self.project_repo.get(eval_data.project_id)
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

        existing = await self.eval_repo.get_evaluation_for_project_and_judge(eval_data.project_id, judge_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already evaluated this project",
            )

        criterion_ids = [item.criterion_id for item in eval_data.scores]
        if len(set(criterion_ids)) != len(criterion_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate criteria are not allowed",
            )

        result = await self.db.execute(
            select(Criterion)
            .options(noload("*"))
            .join(
                ChallengeCategory,
                Criterion.challenge_category_id == ChallengeCategory.id,
            )
            .where(Criterion.id.in_(criterion_ids), ChallengeCategory.event_id == event_id)
        )
        criteria = {criterion.id: criterion for criterion in result.scalars().all()}

        if project.challenge_id is not None:
            challenge = await self.db.scalar(
                select(Challenge).options(noload("*")).where(Challenge.id == project.challenge_id)
            )
            criteria = {
                criterion_id: criterion
                for criterion_id, criterion in criteria.items()
                if criterion.challenge_category_id == challenge.category_id
            }

        total_score = 0.0
        for score_item in eval_data.scores:
            criterion = criteria.get(score_item.criterion_id)
            if criterion is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Criterion {score_item.criterion_id} does not belong to this project",
                )
            if score_item.score > criterion.max_score:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Score exceeds the maximum for criterion {criterion.name}",
                )
            total_score += score_item.score * criterion.weight

        evaluation = await self.eval_repo.create(
            project_id=eval_data.project_id,
            judge_id=judge_id,
            comment=eval_data.comment,
            total_score=total_score,
        )

        for score_item in eval_data.scores:
            score = EvaluationScore(
                evaluation_id=evaluation.id,
                criterion_id=score_item.criterion_id,
                score=score_item.score,
            )
            self.db.add(score)

        await self.db.flush()
        await self.db.refresh(evaluation)
        from app.services.ranking_service import RankingService

        await RankingService(self.db).invalidate_cache(event_id)
        return evaluation

    async def get_project_evaluations(self, event_id: UUID, project_id: UUID) -> List[Evaluation]:
        project = await self.project_repo.get(project_id)
        if project is None or project.event_id != event_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
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
