from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EvaluationScoreCreate(BaseModel):
    criterion_id: UUID
    score: float = Field(..., ge=0)


class EvaluationCreate(BaseModel):
    project_id: UUID
    comment: Optional[str] = None
    scores: List[EvaluationScoreCreate] = Field(..., min_length=1)


class EvaluationScoreResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    criterion_id: UUID
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
    id: UUID
    project_id: UUID
    judge_id: UUID
    comment: Optional[str] = None
    total_score: float
    submitted_at: datetime
    scores: List[EvaluationScoreResponse] = []

    model_config = {"from_attributes": True}


class RankResponse(BaseModel):
    position: int
    project_id: UUID
    project_name: str
    team_id: UUID
    team_name: str
    total_score: float
    evaluation_count: int
