import json
import logging
from typing import Any, Optional

import aio_pika

from .config import MQConfig, ConfigurationManager

logger = logging.getLogger(__name__)


class MessageSender:
    def __init__(self, config: Optional[MQConfig] = None):
        self.config = config or ConfigurationManager.get_config()
        self.connection = None
        self.channel = None

    async def setup(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.config.connection_url)
            self.channel = await self.connection.channel()

    async def send_messages(self, messages: list[dict[str, Any]]):
        """
        发送消息到指定队列

        Args:
            messages: 消息列表，每个消息是一个字典，包含 queue_name 和 message 字段
        """
        if not messages:
            return

        await self.setup()
        
        for msg in messages:
            try:
                queue_name = msg["queue_name"]
                payload = json.dumps(msg["message"]).encode()

                await self.channel.default_exchange.publish(
                    aio_pika.Message(body=payload, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key=queue_name,
                )
                logger.info(f"Sent message to queue: {queue_name}")

            except Exception as e:
                logger.exception(f"Failed to send message to {msg.get('queue_name')}: {e}")

    async def close(self):
        """关闭连接"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None


# 为了保持向后兼容性，保留原有的函数
async def send_messages(messages: list[dict[str, Any]], channel: aio_pika.Channel):
    """
    发送消息到指定队列（旧版本兼容函数）

    Args:
        messages: 消息列表，每个消息是一个字典，包含 queue_name 和 message 字段
        channel: RabbitMQ channel 对象
    """
    if not messages:
        return

    for msg in messages:
        try:
            queue_name = msg["queue_name"]
            payload = json.dumps(msg["message"]).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(body=payload, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
            logger.info(f"Sent message to queue: {queue_name}")

        except Exception as e:
            logger.exception(f"Failed to send message to {msg.get('queue_name')}: {e}")
