from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationCategory
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_unread_by_user(self, user_id: UUID) -> List[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.read == False)
            .order_by(Notification.sent_at.desc())
        )
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification:
            notification.read = True
            notification.read_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: UUID) -> int:
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read == False)
            .values(read=True, read_at=datetime.utcnow())
            .returning(func.count(Notification.id))
        )
        await self.db.flush()
        return result.scalar() or 0

    async def get_by_category(self, user_id: UUID, category: NotificationCategory) -> List[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.category == category)
            .order_by(Notification.sent_at.desc())
        )
        return list(result.scalars().all())

    async def count_unread(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id, Notification.read == False
            )
        )
        return result.scalar() or 0
