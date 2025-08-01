import asyncio
import json
from collections.abc import Callable
from typing import Any, Optional
from functools import wraps

import aio_pika
import redis.asyncio as redis
import logging

from .config import MQConfig, ConfigurationManager
from .sender import send_messages

logger = logging.getLogger(__name__)


class RedisAggregator:
    def __init__(self, redis_url: str, sources: list[str], message_ttl: int = 86400):
        self.redis_url = redis_url
        self.sources = set(sources)
        self.redis = None
        self.message_ttl = message_ttl

    async def setup(self):
        if not self.redis:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def aggregate(self, source, task_id, body):
        await self.setup()
        key = f"agg:{task_id}"
        logger.info(f"Aggregating {source} for {task_id}")
        await self.redis.hset(key, source, json.dumps(body))
        await self.redis.expire(key, self.message_ttl)
        fields = await self.redis.hkeys(key)
        if set(fields) == self.sources:
            all_msgs = await self.redis.hgetall(key)
            await self.redis.delete(key)
            return [json.loads(all_msgs[src]) for src in self.sources]
        return None


class ConsumerManager:
    def __init__(
        self, 
        main_func: Callable[[list[Any]], Any | list[Any]], 
        listen_queues: list[str], 
        send_queues: list[str],
        config: Optional[MQConfig] = None,
    ):
        self.main_func = main_func
        self.listen_queues = listen_queues
        self.send_queues = send_queues
        self._config = config
        self.use_redis_agg = len(listen_queues) > 1
        self.aggregator = None

    @property
    def config(self) -> MQConfig:
        """延迟获取配置，直到真正需要时才获取"""
        if not hasattr(self, '_resolved_config'):
            self._resolved_config = self._config or ConfigurationManager.get_config()
            # 初始化聚合器
            if self.use_redis_agg:
                if not self._resolved_config.aggregator_url:
                    raise ValueError("Redis aggregator URL is required when using multiple listen queues")
                self.aggregator = RedisAggregator(
                    redis_url=self._resolved_config.aggregator_url, 
                    sources=self.listen_queues,
                    message_ttl=self._resolved_config.message_ttl
                )
        return self._resolved_config

    async def _wrapper(self):
        # 这里使用 self.config 属性来确保配置已经被正确初始化
        connection = await aio_pika.connect_robust(self.config.connection_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=self.config.prefetch_count)

        for idx, queue_name in enumerate(self.listen_queues):
            queue = await channel.declare_queue(queue_name, durable=True)

            async def handler(msg: aio_pika.IncomingMessage, qidx=idx, queue_name=queue_name):
                try:
                    async with msg.process():
                        try:
                            body = json.loads(msg.body.decode())
                        except Exception as e:
                            logger.error(f"Failed to decode message from {queue_name}: {e}")
                            return

                        task_id = body.get("task_id")
                        if not task_id:
                            logger.warning(f"Missing task_id in message from {queue_name}")
                            return

                        if self.use_redis_agg:
                            # 用Redis聚合
                            agg_result = await self.aggregator.aggregate(queue_name, task_id, body)
                            if agg_result is None:
                                return
                            messages = agg_result
                        else:
                            # 单队列，直接处理
                            messages = [body]
                        try:
                            result = await self.main_func(messages)
                            if result is None:
                                return
                            results = result if isinstance(result, list) else [result]

                            if len(results) != len(self.send_queues):
                                logger.warning(f"Expected {len(self.send_queues)} outputs, got {len(results)}")
                                return

                            outbound = [
                                {"queue_name": self.send_queues[i], "message": results[i]} for i in range(len(results))
                            ]
                            await send_messages(outbound, channel)

                        except asyncio.CancelledError:
                            logger.warning(f"Task {task_id} was cancelled")
                            await msg.nack(requeue=True)
                            return
                        except Exception as e:
                            logger.exception(f"Exception in main: {e}")
                            await msg.nack(requeue=True)
                            return
                except Exception as e:
                    logger.exception("Critical error in message handler")

            await queue.consume(handler)
            logger.info(f"Consuming from queue: {queue_name}")

        logger.info("All consumers started.")
        await asyncio.Future()

    def start(self):
        """启动消费者"""
        try:
            asyncio.run(self._wrapper())
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user.")

    def __call__(self, *args, **kwargs):
        """支持直接调用"""
        return self.main_func(*args, **kwargs)


def start_consumer(  # noqa: ANN201
    listen_queues: list[str],
    send_queues: list[str],
    config: Optional[MQConfig] = None,
):
    """
    装饰器函数，用于创建和启动消息消费者

    Args:
        listen_queues: 要监听的队列列表
        send_queues: 要发送消息的队列列表
        config: 可选的MQ配置，如果不提供则使用全局配置

    Example:
        @start_consumer(
            listen_queues=["input_queue"],
            send_queues=["output_queue"],
            config=MQConfig(
                connection_url="amqp://guest:guest@localhost/",
                prefetch_count=10
            )
        )
        async def process_message(messages: list[dict]) -> Any:
            # 处理消息
            return result
    """
    def decorator(main: Callable[[list[Any]], Any | list[Any]]):
        # 创建一个包装函数，延迟 ConsumerManager 的初始化
        @wraps(main)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, '_consumer'):
                wrapper._consumer = ConsumerManager(main, listen_queues, send_queues, config)
            return wrapper._consumer(*args, **kwargs)
        
        # 添加 start 方法
        wrapper.start = lambda: wrapper._consumer.start() if hasattr(wrapper, '_consumer') else ConsumerManager(main, listen_queues, send_queues, config).start()
        
        return wrapper

    return decorator
