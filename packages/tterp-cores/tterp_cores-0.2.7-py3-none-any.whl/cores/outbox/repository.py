# cores/outbox/repository.py
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import OutboxEvent, OutboxEventStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(self, event: OutboxEvent):
        """Thêm một event vào outbox.
        Hàm này phải được gọi bên trong một transaction đang mở."""
        self.session.add(event)
        await self.session.flush() # Đảm bảo event được đưa vào session

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Lấy các event đang chờ xử lý."""
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxEventStatus.PENDING)
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True) # Tránh nhiều worker lấy cùng lúc
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_processed(self, event_id: uuid.UUID):
        """Đánh dấu event đã được xử lý thành công."""
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(status=OutboxEventStatus.PROCESSED, processed_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
