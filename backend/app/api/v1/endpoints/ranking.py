import json
import asyncio
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db
from app.schemas.evaluation import RankResponse
from app.services.ranking_service import RankingService

router = APIRouter(prefix="/events/{event_id}/ranking", tags=["Ranking"])


@router.get("/", response_model=List[RankResponse])
async def get_ranking(event_id: UUID, db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    return await service.calculate_ranking(event_id)


@router.get("/stream")
async def stream_ranking(event_id: UUID, db: AsyncSession = Depends(get_db)):
    async def event_generator():
        while True:
            try:
                service = RankingService(db)
                rankings = await service.calculate_ranking(event_id)
                yield {
                    "event": "ranking_update",
                    "data": json.dumps([r.model_dump() for r in rankings], default=str),
                }
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception:
                yield {"event": "error", "data": "Error fetching ranking"}
                await asyncio.sleep(60)

    return EventSourceResponse(event_generator())
