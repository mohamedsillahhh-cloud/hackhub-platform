from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_organizer, require_event_manager
from app.models.challenge import Challenge, ChallengeCategory, Criterion
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.challenge import (
    ChallengeCategoryCreate,
    ChallengeCategoryResponse,
    ChallengeCreate,
    ChallengeResponse,
    CriterionCreate,
    CriterionResponse,
)

router = APIRouter(prefix="/events/{event_id}/challenges", tags=["Challenges"])


async def _get_category(db: AsyncSession, event_id: UUID, category_id: UUID) -> ChallengeCategory:
    result = await db.execute(
        select(ChallengeCategory).where(
            ChallengeCategory.id == category_id,
            ChallengeCategory.event_id == event_id,
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("/", response_model=List[ChallengeResponse])
async def list_challenges(event_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Challenge).where(Challenge.event_id == event_id).order_by(Challenge.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    event_id: UUID,
    challenge_data: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    await require_event_manager(db, event_id, current_user)
    category_id = UUID(challenge_data.category_id)
    await _get_category(db, event_id, category_id)
    return await BaseRepository(Challenge, db).create(
        event_id=event_id,
        category_id=category_id,
        title=challenge_data.title,
        description=challenge_data.description,
        requirements=challenge_data.requirements,
        documentation_url=challenge_data.documentation_url,
    )


@router.post(
    "/categories",
    response_model=ChallengeCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    event_id: UUID,
    category_data: ChallengeCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    await require_event_manager(db, event_id, current_user)
    return await BaseRepository(ChallengeCategory, db).create(
        event_id=event_id,
        name=category_data.name,
        description=category_data.description,
        order=category_data.order,
    )


@router.get("/categories", response_model=List[ChallengeCategoryResponse])
async def list_categories(event_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChallengeCategory).where(ChallengeCategory.event_id == event_id).order_by(ChallengeCategory.order)
    )
    return list(result.scalars().all())


@router.post("/criteria", response_model=CriterionResponse, status_code=status.HTTP_201_CREATED)
async def create_criterion(
    event_id: UUID,
    criterion_data: CriterionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    await require_event_manager(db, event_id, current_user)
    category_id = UUID(criterion_data.challenge_category_id)
    await _get_category(db, event_id, category_id)
    return await BaseRepository(Criterion, db).create(
        challenge_category_id=category_id,
        name=criterion_data.name,
        description=criterion_data.description,
        max_score=criterion_data.max_score,
        weight=criterion_data.weight,
    )


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(event_id: UUID, challenge_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Challenge).where(Challenge.id == challenge_id, Challenge.event_id == event_id))
    challenge = result.scalar_one_or_none()
    if challenge is None:
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
    await require_event_manager(db, event_id, current_user)
    challenge = await get_challenge(event_id, challenge_id, db)
    category_id = UUID(challenge_data.category_id)
    await _get_category(db, event_id, category_id)
    updated = await BaseRepository(Challenge, db).update(
        challenge.id,
        title=challenge_data.title,
        description=challenge_data.description,
        requirements=challenge_data.requirements,
        documentation_url=challenge_data.documentation_url,
        category_id=category_id,
    )
    return updated


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
    event_id: UUID,
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_organizer),
):
    await require_event_manager(db, event_id, current_user)
    challenge = await get_challenge(event_id, challenge_id, db)
    await BaseRepository(Challenge, db).delete(challenge.id)
