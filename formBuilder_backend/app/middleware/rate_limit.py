"""Middleware de rate limiting"""

from datetime import datetime, timedelta
from typing import Dict


class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Vérifier si une requête est autorisée"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        if key not in self.requests:
            self.requests[key] = []

        # Nettoyer les anciennes requêtes
        self.requests[key] = [
            req_time for req_time in self.requests[key] if req_time > cutoff
        ]

        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True
        return False


rate_limiter = RateLimiter()
