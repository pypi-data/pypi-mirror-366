"""Main client for the Sovant SDK."""

from typing import Any, Dict, Union

from .base_client import AsyncBaseClient, BaseClient
from .resources import AsyncMemories, AsyncThreads, Memories, Threads
from .types import Config


class SovantClient:
    """Synchronous client for the Sovant API."""
    
    def __init__(self, api_key: Union[str, Config, None] = None):
        """
        Initialize the Sovant client.
        
        Args:
            api_key: API key string, Config object, or None (uses env var)
        """
        if api_key is None:
            import os
            api_key = os.environ.get("SOVANT_API_KEY", "")
        
        if isinstance(api_key, str):
            config = Config(api_key=api_key)
        else:
            config = api_key
        
        self.memories = Memories(config)
        self.threads = Threads(config)
        self._config = config
    
    def ping(self) -> Dict[str, str]:
        """Test API connection."""
        client = BaseClient(self._config)
        return client.request("GET", "/health")
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current API usage and quota."""
        client = BaseClient(self._config)
        return client.request("GET", "/usage")


class AsyncSovantClient:
    """Asynchronous client for the Sovant API."""
    
    def __init__(self, api_key: Union[str, Config, None] = None):
        """
        Initialize the async Sovant client.
        
        Args:
            api_key: API key string, Config object, or None (uses env var)
        """
        if api_key is None:
            import os
            api_key = os.environ.get("SOVANT_API_KEY", "")
        
        if isinstance(api_key, str):
            config = Config(api_key=api_key)
        else:
            config = api_key
        
        self.memories = AsyncMemories(config)
        self.threads = AsyncThreads(config)
        self._config = config
    
    async def ping(self) -> Dict[str, str]:
        """Test API connection."""
        async with AsyncBaseClient(self._config) as client:
            return await client.request("GET", "/health")
    
    async def get_usage(self) -> Dict[str, Any]:
        """Get current API usage and quota."""
        async with AsyncBaseClient(self._config) as client:
            return await client.request("GET", "/usage")
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Clean up any open connections
        if hasattr(self.memories, "client"):
            await self.memories.client.aclose()
        if hasattr(self.threads, "client"):
            await self.threads.client.aclose()