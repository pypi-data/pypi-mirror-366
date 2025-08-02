# src/cores/outbox/worker.py
import asyncio
import json
import logging

import aio_pika
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..events.event_bus import RabbitMQEventBus
from .repository import OutboxRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class OutboxRelayWorker:
    """
    Lớp worker có thể tái sử dụng để xử lý các event trong outbox.
    Chứa logic cốt lõi, độc lập với bất kỳ service cụ thể nào.
    """
    def __init__(self, session_factory: async_sessionmaker, poll_interval: int = 5):
        """
        Khởi tạo worker.
        :param session_factory: Một async_sessionmaker để tạo session DB.
        :param poll_interval: Khoảng thời gian (giây) giữa các lần quét.
        """
        self.session_factory = session_factory
        self.poll_interval = poll_interval
        self.event_bus = RabbitMQEventBus()

    async def _process_batch(self):
        """Xử lý một batch các event."""
        await self.event_bus.connect()
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    outbox_repo = OutboxRepository(session)
                    pending_events = await outbox_repo.get_pending_events(limit=100)

                    if not pending_events:
                        return

                    logging.info(
                        f"Found {len(pending_events)} pending events. Publishing..."
                    )

                    for event_model in pending_events:
                        try:
                            message_body = json.dumps({
                                "event_id": str(event_model.id),
                                "event_name": event_model.topic,
                                "created_at": event_model.created_at.isoformat(),
                                "payload": event_model.payload
                            }).encode()

                            message = aio_pika.Message(
                                body=message_body,
                                content_type="application/json",
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                message_id=str(event_model.id)
                            )

                            await self.event_bus.exchange.publish(
                                message, routing_key=event_model.topic
                            )
                            await outbox_repo.mark_as_processed(event_model.id)
                            logging.info(
                                f"Published and marked event {event_model.id} as "
                                f"PROCESSED."
                            )

                        except Exception as e:
                            logging.error(
                                f"Failed to publish event {event_model.id}: {e}",
                                exc_info=True,
                            )
                await session.commit()
        except Exception as e:
            logging.error(
                f"An error occurred while processing outbox batch: {e}",
                exc_info=True,
            )
        finally:
            await self.event_bus.disconnect()

    async def run(self):
        """Bắt đầu vòng lặp vô hạn của worker."""
        logging.info(
            f"Starting Outbox Relay Worker. "
            f"Polling every {self.poll_interval} seconds."
        )
        while True:
            await self._process_batch()
            await asyncio.sleep(self.poll_interval)
