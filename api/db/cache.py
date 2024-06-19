# pylint: disable=C0301
import logging

from redis.asyncio.client import Redis as RedisClient
from redis.asyncio.client import StrictRedis

from api.settings import env


class Redis:
    redis_: RedisClient

    def __init__(self):
        self.redis_ = None  # type: ignore

    async def init(self):
        redis_ = StrictRedis(
            host=env.redis_host,
            port=env.redis_port,
            password=env.redis_password,
            db=env.redis_db,
            decode_responses=True,
            encoding="utf-8",
        )
        logging.info("redis connection initializing")
        self.redis_ = await redis_.initialize()
        logging.info("redis connection initialized")

    async def close(self):
        await self.redis_.close()

    def get_redis(self):
        return self.redis_

    def mangle_key(self, namespace, key):
        return f"{env.environment}:{namespace}:{key}"


# NOTE: 커넥션 비용을 줄이기 위해 싱글톤으로 사용
redis = Redis()
