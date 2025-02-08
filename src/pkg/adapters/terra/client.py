import aiohttp
from typing import Dict, Any, Optional


class Client:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self._base_url = base_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: Optional[str] = None  # Token will be fetched asynchronously

    async def _get_token(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/auth/token",
                json={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            ) as response:
                data = await response.json()
                self._token = data.get("accessToken")
                return self._token

    async def _ensure_token(self):
        """Ensure token is available before making requests"""
        if not self._token:
            token = await self._get_token()

    async def fetch_collections(self) -> Dict[str, Any]:
        await self._ensure_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/collections",
                headers={"Authorization": f"Bearer {self._token}"},
            ) as response:
                return await response.json()

    async def fetch_collection(self, collection_id: str) -> Dict[str, Any]:
        await self._ensure_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/collections/{collection_id}",
                headers={"Authorization": f"Bearer {self._token}"},
            ) as response:
                return await response.json()

    async def fetch_collection_feature(
        self,
        collection_id: str,
        feature_id: str,
    ) -> Dict[str, Any]:
        await self._ensure_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self._base_url}/collections/{collection_id}/features/{feature_id}",
                headers={"Authorization": f"Bearer {self._token}"},
            ) as response:
                wrapped_feature = await response.json()
                return wrapped_feature.get("feature")
