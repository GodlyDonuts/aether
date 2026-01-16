import secrets
import json
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from backend.redis_client import RedisClient

class APIKey(BaseModel):
    id: str
    name: str
    key: str
    created_at: str
    status: str = "active"
    usage_month: int = 0
    usage_limit: int = 100000

class KeyStore:
    def __init__(self):
        pass

    async def _get_redis(self):
        return RedisClient.get_instance()

    async def list_keys(self) -> List[APIKey]:
        redis = await self._get_redis()
        key_ids = await redis.smembers("apikeys:index")
        
        keys = []
        for kid in key_ids:
            data = await redis.hgetall(f"apikey:{kid}")
            if data:
                # Redis returns strings, cast ints if needed
                if "usage_month" in data:
                    data["usage_month"] = int(data["usage_month"])
                if "usage_limit" in data:
                    data["usage_limit"] = int(data["usage_limit"])
                keys.append(APIKey(**data))
        
        # Sort by created_at desc
        keys.sort(key=lambda x: x.created_at, reverse=True)
        return keys

    async def create_key(self, name: str) -> APIKey:
        redis = await self._get_redis()
        
        # Generate secure key
        token = f"sk_live_{secrets.token_urlsafe(24)}"
        key_id = secrets.token_hex(4)
        
        new_key = {
            "id": key_id,
            "name": name,
            "key": token,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "active",
            "usage_month": 0,
            "usage_limit": 100000
        }
        
        # Save to hash
        await redis.hset(f"apikey:{key_id}", mapping=new_key)
        # Add to index
        await redis.sadd("apikeys:index", key_id)
        
        return APIKey(**new_key)

    async def revoke_key(self, key_id: str) -> bool:
        redis = await self._get_redis()
        exists = await redis.exists(f"apikey:{key_id}")
        if not exists:
            return False
            
        await redis.hset(f"apikey:{key_id}", "status", "revoked")
        return True

# Global store instance
store = KeyStore()
