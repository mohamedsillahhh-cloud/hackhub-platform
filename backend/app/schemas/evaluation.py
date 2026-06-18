from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EvaluationScoreCreate(BaseModel):
    criterion_id: str
    score: float = Field(..., ge=0)


class EvaluationCreate(BaseModel):
    project_id: str
    comment: Optional[str] = None
    scores: List[EvaluationScoreCreate]


class EvaluationScoreResponse(BaseModel):
    id: str
    evaluation_id: str
    criterion_id: str
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
    id: str
    project_id: str
    judge_id: str
    comment: Optional[str] = None
    total_score: float
    submitted_at: datetime
    scores: List[EvaluationScoreResponse] = []

    model_config = {"from_attributes": True}


class RankResponse(BaseModel):
    position: int
    project_id: str
    project_name: str
    team_id: str
    team_name: str
    total_score: float
    evaluation_count: int
