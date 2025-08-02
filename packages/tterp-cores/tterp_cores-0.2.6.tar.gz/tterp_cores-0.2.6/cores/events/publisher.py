
# cores/events/publisher.py
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..outbox.models import OutboxEvent
from ..outbox.repository import OutboxRepository
from .event_bus import EventBus
from .interfaces import IEventPublisher
from .schemas.base_event import Event


class OutboxEventPublisher(IEventPublisher):
    """
    Triển khai IEventPublisher để ghi event vào bảng Outbox trong cùng một transaction.
    Đây là lựa chọn mặc định cho các hành động nghiệp vụ cần đảm bảo tính toàn vẹn.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.outbox_repo = OutboxRepository(self.session)

    async def publish(self, event: Event):
        """Ghi một event vào bảng outbox."""
        # Trích xuất payload từ Pydantic model
        payload_dict = event.model_dump(mode='json').get('payload', {})

        outbox_event = OutboxEvent(
            aggregate_id=str(payload_dict.get("item_id") or event.event_id),
            topic=event.event_name,
            payload=payload_dict
        )
        await self.outbox_repo.add_event(outbox_event)

    async def publish_many(self, events: list[Event]):
        """Ghi nhiều event vào bảng outbox."""
        for event in events:
            await self.publish(event)

class DirectEventPublisher(IEventPublisher):
    """
    Triển khai IEventPublisher để gửi event trực tiếp ra Message Broker.
    Sử dụng cho các event không yêu cầu transactional integrity hoặc để
    tương thích ngược.
    """
    def __init__(self, bus: EventBus):
        self.bus = bus

    async def publish(self, event: Event):
        """Gửi event trực tiếp qua EventBus."""
        await self.bus.publish(event)

    async def publish_many(self, events: list[Event]):
        """Gửi nhiều event trực tiếp qua EventBus."""
        for event in events:
            await self.bus.publish(event)
