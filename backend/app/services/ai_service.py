from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.event_repository import EventRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


try:
    import redis.asyncio as aioredis
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    _redis = None


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = EventRepository(db)
        self.project_repo = ProjectRepository(db)
        self.user_repo = UserRepository(db)

    async def check_daily_token_limit(self, user_id: str) -> bool:
        if _redis is None or not settings.AI_DAILY_TOKEN_LIMIT:
            return True
        today = date.today().isoformat()
        key = f"ai:usage:{user_id}:{today}"
        current = await _redis.get(key)
        if current and int(current) >= settings.AI_DAILY_TOKEN_LIMIT:
            return False
        return True

    async def track_token_usage(self, user_id: str, tokens: int) -> None:
        if _redis is None:
            return
        today = date.today().isoformat()
        key = f"ai:usage:{user_id}:{today}"
        await _redis.incrby(key, tokens)
        await _redis.expire(key, 86400)

    async def _query_openai(self, system_prompt: str, user_message: str, user_id: str = "anonymous") -> str:
        if not settings.OPENAI_API_KEY:
            return "AI assistant is not configured. Please set OPENAI_API_KEY."

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            tokens = response.usage.total_tokens if response.usage else 0
            await self.track_token_usage(user_id, tokens)
            return response.choices[0].message.content or "No response generated."
        except Exception as e:
            return f"AI service error: {str(e)}"

    async def get_event_assistant(self, event_id: UUID, question: str) -> str:
        event = await self.event_repo.get(event_id)
        if not event:
            return "Event not found."

        context_parts = []
        context_parts.append(f"Event: {event.title}")
        context_parts.append(f"Description: {event.description or 'N/A'}")
        context_parts.append(f"Start: {event.start_date}, End: {event.end_date}")
        context_parts.append(f"Location: {event.location or 'Online'}")

        if event.faq:
            if isinstance(event.faq, list):
                for faq_item in event.faq:
                    q = faq_item.get("question", faq_item.get("q", ""))
                    a = faq_item.get("answer", faq_item.get("a", ""))
                    if q and a:
                        context_parts.append(f"FAQ - Q: {q} A: {a}")

        if event.regulations:
            context_parts.append(f"Regulations: {event.regulations[:500]}")

        if event.schedule:
            context_parts.append(f"Schedule: {event.schedule}")

        context = "\n".join(context_parts)

        system_prompt = (
            "You are a helpful event assistant for a hackathon platform called HackHub. "
            "Answer questions based on the event information provided. "
            "If you don't know the answer, say so politely. Keep responses concise and helpful."
        )
        user_message = f"Event information:\n{context}\n\nQuestion: {question}"

        return await self._query_openai(system_prompt, user_message)

    async def assist_evaluation(self, project_id: UUID) -> str:
        project = await self.project_repo.get(project_id)
        if not project:
            return "Project not found."

        context_parts = []
        context_parts.append(f"Project Name: {project.name}")
        context_parts.append(f"Description: {project.description or 'N/A'}")
        context_parts.append(f"GitHub URL: {project.github_url or 'N/A'}")
        context_parts.append(f"Tech Stack: {', '.join(project.tech_stack) if project.tech_stack else 'N/A'}")

        context = "\n".join(context_parts)

        system_prompt = (
            "You are an expert hackathon judge. Analyze the following project and provide constructive feedback. "
            "Evaluate: innovation, technical complexity, completeness, presentation, and impact. "
            "Provide a score out of 100 and specific improvement suggestions."
        )
        user_message = f"Project Details:\n{context}\n\nPlease evaluate this project."

        return await self._query_openai(system_prompt, user_message)

    async def suggest_teams(self, event_id: UUID) -> list:
        participants, _ = await self.user_repo.list_users_paginated(
            limit=200,
            role=None,
        )

        if len(participants) < 2:
            return []

        scored_participants = []
        for p in participants:
            score = 0
            if p.skills:
                score += len(p.skills) * 2
            if p.preferred_languages:
                score += len(p.preferred_languages)
            if p.preferred_frameworks:
                score += len(p.preferred_frameworks)
            if p.experience_level:
                exp_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                score += exp_map.get(p.experience_level.lower(), 0)
            scored_participants.append({
                "user_id": str(p.id),
                "username": p.username,
                "full_name": p.full_name,
                "skills": p.skills or [],
                "languages": p.preferred_languages or [],
                "frameworks": p.preferred_frameworks or [],
                "experience_level": p.experience_level,
                "score": score,
            })

        scored_participants.sort(key=lambda x: x["score"], reverse=True)

        teams = []
        team_size = 3
        for i in range(0, len(scored_participants), team_size):
            team_members = scored_participants[i:i + team_size]
            if len(team_members) >= 2:
                team_skills = set()
                for m in team_members:
                    team_skills.update(m["skills"])
                teams.append({
                    "members": team_members,
                    "combined_skills": list(team_skills),
                    "average_score": sum(m["score"] for m in team_members) / len(team_members),
                })

        return teams
