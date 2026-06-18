from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, RankResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/events/{event_id}/evaluations", tags=["Evaluations"])


@router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def submit_evaluation(
    event_id: UUID,
    eval_data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.JUDGE and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only judges can submit evaluations",
        )
    service = EvaluationService(db)
    return await service.submit_evaluation(event_id, eval_data, current_user.id)


@router.get("/projects/{project_id}", response_model=List[EvaluationResponse])
async def get_project_evaluations(
    event_id: UUID,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = EvaluationService(db)
    return await service.get_project_evaluations(project_id)


@router.get("/ranking", response_model=List[RankResponse])
async def get_ranking(event_id: UUID, db: AsyncSession = Depends(get_db)):
    service = EvaluationService(db)
    return await service.get_ranking(event_id)


@router.get("/my", response_model=List[EvaluationResponse])
async def get_my_evaluations(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.repositories.evaluation_repository import EvaluationRepository
    repo = EvaluationRepository(db)
    return await repo.get_by_judge(current_user.id, event_id)
