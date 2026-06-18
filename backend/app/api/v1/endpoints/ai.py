from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_active_user, get_current_organizer
from app.models.user import User, UserRole
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])
limiter = Limiter(key_func=get_remote_address)


class AskRequest(BaseModel):
    question: str


def get_current_user_id(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if token:
        from app.core.security import decode_token
        payload = decode_token(token)
        if payload:
            return str(payload.get("sub", "anonymous"))
    return "anonymous"


def _is_organizer_or_admin(current_user: User) -> bool:
    return current_user.role in (UserRole.ADMIN, UserRole.ORGANIZER)


@router.post("/events/{event_id}/ask")
@limiter.limit(settings.AI_RATE_LIMIT_ASK)
async def ask_event_assistant(
    request: Request,
    event_id: UUID,
    body: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AIService(db)
    allowed = await service.check_daily_token_limit(str(current_user.id))
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily AI token limit reached")
    answer = await service.get_event_assistant(event_id, body.question)
    return {"answer": answer}


@router.post("/evaluate/{project_id}")
@limiter.limit(settings.AI_RATE_LIMIT_EVALUATE)
async def ai_evaluate(
    request: Request,
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not _is_organizer_or_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizers and admins can use AI evaluation")
    service = AIService(db)
    feedback = await service.assist_evaluation(project_id)
    return {"feedback": feedback}


@router.post("/events/{event_id}/suggest-teams")
@limiter.limit(settings.AI_RATE_LIMIT_SUGGEST)
async def suggest_teams(
    request: Request,
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not _is_organizer_or_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organizers and admins can suggest teams")
    service = AIService(db)
    suggestions = await service.suggest_teams(event_id)
    return {"suggestions": suggestions}
