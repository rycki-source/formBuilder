"""Service de cache Redis"""
import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """Connecter à Redis"""
        self.redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        """Déconnecter de Redis"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            return json.loads(value) if not isinstance(value, dict) else value
        return None
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Stocker une valeur en cache"""
        if not self.redis:
            return
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        """Supprimer une valeur du cache"""
        if not self.redis:
            return
        await self.redis.delete(key)

cache_service = CacheService()