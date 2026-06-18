from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_organizer
from app.models.challenge import Challenge, ChallengeCategory, Criterion
from app.models.user import User
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
    ChallengeCategoryCreate,
    ChallengeCategoryResponse,
    CriterionCreate,
    CriterionResponse,
)
from app.repositories.base import BaseRepository

router = APIRouter(prefix="/events/{event_id}/challenges", tags=["Challenges"])


@router.get("/", response_model=List[ChallengeResponse])
async def list_challenges(event_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Challenge).where(Challenge.event_id == event_id).order_by(Challenge.created_at.desc())
    )
    challenges = result.scalars().all()
    return challenges


@router.post("/", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    event_id: UUID,
    challenge_data: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    repo = BaseRepository(Challenge, db)
    category_result = await db.execute(
        select(ChallengeCategory).where(ChallengeCategory.id == UUID(challenge_data.category_id))
    )
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    challenge = await repo.create(
        event_id=event_id,
        category_id=UUID(challenge_data.category_id),
        title=challenge_data.title,
        description=challenge_data.description,
        requirements=challenge_data.requirements,
        documentation_url=challenge_data.documentation_url,
    )
    return challenge


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(event_id: UUID, challenge_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(Challenge, db)
    challenge = await repo.get(challenge_id)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return challenge


@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(
    event_id: UUID,
    challenge_id: UUID,
    challenge_data: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    repo = BaseRepository(Challenge, db)
    updated = await repo.update(
        challenge_id,
        title=challenge_data.title,
        description=challenge_data.description,
        requirements=challenge_data.requirements,
        documentation_url=challenge_data.documentation_url,
        category_id=UUID(challenge_data.category_id),
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return updated


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
    event_id: UUID,
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    repo = BaseRepository(Challenge, db)
    deleted = await repo.delete(challenge_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")


@router.post("/categories", response_model=ChallengeCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    event_id: UUID,
    category_data: ChallengeCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    repo = BaseRepository(ChallengeCategory, db)
    category = await repo.create(
        event_id=event_id,
        name=category_data.name,
        description=category_data.description,
        order=category_data.order,
    )
    return category


@router.get("/categories", response_model=List[ChallengeCategoryResponse])
async def list_categories(event_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChallengeCategory).where(ChallengeCategory.event_id == event_id).order_by(ChallengeCategory.order)
    )
    categories = result.scalars().all()
    return categories


@router.post("/criteria", response_model=CriterionResponse, status_code=status.HTTP_201_CREATED)
async def create_criterion(
    event_id: UUID,
    criterion_data: CriterionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    repo = BaseRepository(Criterion, db)
    criterion = await repo.create(
        challenge_category_id=UUID(criterion_data.challenge_category_id),
        name=criterion_data.name,
        description=criterion_data.description,
        max_score=criterion_data.max_score,
        weight=criterion_data.weight,
    )
    return criterion
