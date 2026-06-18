import json
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from app.repositories.evaluation_repository import EvaluationRepository
from app.schemas.evaluation import RankResponse


class RankingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.eval_repo = EvaluationRepository(db)
        self._redis = None

    async def _get_redis(self):
        if self._redis is None and aioredis and settings.REDIS_URL:
            try:
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None
        return self._redis

    async def calculate_ranking(self, event_id: UUID) -> List[RankResponse]:
        redis_client = await self._get_redis()
        cache_key = f"ranking:{event_id}"

        if redis_client:
            cached = await redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                return [RankResponse(**item) for item in data]

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

        if redis_client:
            await redis_client.setex(cache_key, 300, json.dumps([r.model_dump() for r in rankings]))

        return rankings

    async def invalidate_cache(self, event_id: UUID) -> None:
        redis_client = await self._get_redis()
        if redis_client:
            await redis_client.delete(f"ranking:{event_id}")
