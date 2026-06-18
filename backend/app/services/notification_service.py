from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType, NotificationCategory
from app.repositories.notification_repository import NotificationRepository
from app.utils.email import send_email as send_email_util


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notif_repo = NotificationRepository(db)

    async def send_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> Notification:
        notification = await self.notif_repo.create(
            user_id=user_id,
            type=notification_type,
            category=category,
            title=title,
            message=message,
            data=data or {},
        )

        if notification_type == NotificationType.EMAIL:
            from app.models.user import User
            from sqlalchemy import select

            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                html = f"<h2>{title}</h2><p>{message}</p>"
                await send_email_util(to=user.email, subject=title, body_html=html)

        elif notification_type == NotificationType.TELEGRAM:
            from app.core.config import settings

            if settings.TELEGRAM_BOT_TOKEN:
                try:
                    import httpx

                    text = f"*{title}*\n\n{message}"
                    async with httpx.AsyncClient() as client:
                        from app.models.user import User
                        result = await self.db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()
                        if user:
                            await client.post(
                                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                                json={"chat_id": user.username, "text": text, "parse_mode": "Markdown"},
                            )
                except Exception:
                    pass

        return notification

    async def get_unread_notifications(self, user_id: UUID) -> List[Notification]:
        return await self.notif_repo.get_unread_by_user(user_id)

    async def get_all_notifications(self, user_id: UUID, skip: int = 0, limit: int = 50) -> tuple:
        return await self.notif_repo.get_multi(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
            order_by="sent_at",
            descending=True,
        )

    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        return await self.notif_repo.mark_as_read(notification_id)

    async def mark_all_as_read(self, user_id: UUID) -> int:
        return await self.notif_repo.mark_all_as_read(user_id)

    async def count_unread(self, user_id: UUID) -> int:
        return await self.notif_repo.count_unread(user_id)
