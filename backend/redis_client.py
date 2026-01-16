import os
import redis.asyncio as redis
from backend.config import settings

class RedisClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                encoding="utf-8"
            )
        return cls._instance

async def get_redis():
    return RedisClient.get_instance()
