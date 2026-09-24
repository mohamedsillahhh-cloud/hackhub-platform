from pydantic import BaseModel


class PublicDashboardStats(BaseModel):
    total_events: int
    total_projects: int
    total_teams: int
    active_participants: int
