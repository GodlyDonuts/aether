from fastapi import APIRouter, HTTPException, Depends
from backend.data.store import store, APIKey
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

class CreateKeyRequest(BaseModel):
    name: str

class StatsResponse(BaseModel):
    total_requests: int
    active_users: int
    revenue: float
    history: List[dict]

@router.get("/keys", response_model=List[APIKey])
async def get_keys():
    """List all API keys."""
    return await store.list_keys()

@router.post("/keys", response_model=APIKey)
async def create_key(request: CreateKeyRequest):
    """Create a new API key."""
    return await store.create_key(request.name)

@router.delete("/keys/{key_id}")
async def revoke_key(key_id: str):
    """Revoke an API key."""
    success = await store.revoke_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"status": "success"}

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics from Redis.
    """
    from backend.redis_client import RedisClient
    redis = RedisClient.get_instance()
    
    total_requests = int(await redis.get("stats:total_requests") or 0)
    # active_users could be a set of IPs seen in the last hour, but for now just scard
    active_users = int(await redis.scard("stats:active_users") or 0)
    revenue = float(await redis.get("stats:total_revenue") or 0.0)
    
    # Retrieve history from a Redis list (assuming a background worker populates this)
    # For now, return empty if no history implementation exists yet, avoiding mock data.
    # We could implement a simple daily snapshot later.
    history_raw = await redis.lrange("stats:history", 0, 6)
    history = []
    import json
    for h in history_raw:
        try:
            history.append(json.loads(h))
        except:
            pass
            
    # Use empty/zero defaults rather than fake data
    if not history:
        # Return at least empty structure if needed by frontend
        history = []
        
    return StatsResponse(
        total_requests=total_requests,
        active_users=active_users,
        revenue=revenue,
        history=history
    )
