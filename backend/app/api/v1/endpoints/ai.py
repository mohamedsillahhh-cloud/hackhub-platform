from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


class AskRequest(BaseModel):
    question: str


@router.post("/events/{event_id}/ask")
async def ask_event_assistant(
    event_id: UUID,
    request: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AIService(db)
    answer = await service.get_event_assistant(event_id, request.question)
    return {"answer": answer}


@router.post("/evaluate/{project_id}")
async def ai_evaluate(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AIService(db)
    feedback = await service.assist_evaluation(project_id)
    return {"feedback": feedback}


@router.post("/events/{event_id}/suggest-teams")
async def suggest_teams(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AIService(db)
    suggestions = await service.suggest_teams(event_id)
    return {"suggestions": suggestions}
