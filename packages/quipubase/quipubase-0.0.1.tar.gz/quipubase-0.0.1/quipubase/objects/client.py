# quipubase/objects/client.py
"""Objects client"""

import json
import typing as tp

from httpx import AsyncClient

from .typedefs import PubResponse, QuipubaseRequest, SubResponse


class Objects(tp.NamedTuple):
    """Objects client"""

    client: AsyncClient

    async def sub(self, *, collection_id: str):
        """Subscribe to a collection"""
        params = {"stream": True}
        async with self.client.stream(
            "GET", f"/collections/objects/{collection_id}", params=params
        ) as stream_response:
            async for chunk in stream_response.aiter_lines():
                try:
                    string_data = chunk[6:]
                    data = json.loads(string_data)
                    yield SubResponse(**data)
                except (json.JSONDecodeError, IndexError):
                    continue

    async def pub(self, collection_id: str, request: QuipubaseRequest):
        """Publish a request to a collection"""
        response = await self.client.post(
            f"/collections/objects/{collection_id}", json=request.model_dump()
        )
        return PubResponse(**response.json())
