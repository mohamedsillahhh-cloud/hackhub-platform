from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CriterionCreate(BaseModel):
    challenge_category_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    max_score: float = Field(..., gt=0)
    weight: float = 1.0


class CriterionResponse(BaseModel):
    id: str
    challenge_category_id: str
    name: str
    description: Optional[str] = None
    max_score: float
    weight: float

    model_config = {"from_attributes": True}


class ChallengeCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    order: int = 0


class ChallengeCategoryResponse(BaseModel):
    id: str
    event_id: str
    name: str
    description: Optional[str] = None
    order: int
    criteria: List[CriterionResponse] = []

    model_config = {"from_attributes": True}


class ChallengeCreate(BaseModel):
    category_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    documentation_url: Optional[str] = None


class ChallengeResponse(BaseModel):
    id: str
    event_id: str
    category_id: str
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    documentation_url: Optional[str] = None
    created_at: datetime
    category: Optional[ChallengeCategoryResponse] = None

    model_config = {"from_attributes": True}
