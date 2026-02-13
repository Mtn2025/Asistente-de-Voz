"""
Port (Interface) for Distributed Cache.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

class CachePort(ABC):
    """
    Port for cache operations.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in the cache with a Time-To-Live (TTL).
        """
        pass

    @abstractmethod
    async def invalidate(self, pattern: str) -> None:
        """Delete keys matching the given pattern."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the cache connection."""
        pass
