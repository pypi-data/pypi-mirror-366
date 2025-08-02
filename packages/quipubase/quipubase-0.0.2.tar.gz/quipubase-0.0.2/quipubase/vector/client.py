from __future__ import annotations

import typing as tp

from httpx import AsyncClient

from loguru import logger

from .typedefs import (DeleteResponse, EmbedText, Embedding, QueryResponse,
                       QueryText, UpsertResponse)


class Vectors(tp.NamedTuple):
    """Asynchronous client for Quipubase vector endpoints."""

    client: AsyncClient

    async def list(self, *, namespace: str) -> tp.List[str]:
        """
        Get all IDs from a specific namespace.

        Args:
            namespace: The namespace to retrieve IDs from.

        Returns:
            A list of all IDs (strings) within the namespace.
        """
        response = await self.client.get(f"/vector/{namespace}")
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return data

    async def retrieve(self, *, namespace: str, id: str) -> tp.List[Embedding]:
        """
        Get a specific vector by its ID from a namespace.

        Args:
            namespace: The namespace to get the vector from.
            id: The unique identifier of the vector.

        Returns:
            The raw JSON data for the requested vector.
        """
        response = await self.client.get(f"/vector/{namespace}/{id}")
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return [Embedding(**item) for item in data]

    async def upsert(self, *, namespace: str, request: EmbedText) -> UpsertResponse:
        """
        Upsert texts into the vector store.

        This method inserts new texts or updates existing ones, converting them
        to vector embeddings.

        Args:
            namespace: The namespace to upsert the texts into.
            request: An EmbedText object containing the texts to upsert.

        Returns:
            An UpsertResponse object.
        """
        response = await self.client.post(f"/vector/{namespace}", json=request)
        response.raise_for_status()
        return UpsertResponse(**response.json())

    async def query(self, *, namespace: str, request: QueryText) -> QueryResponse:
        """
        Query the vector store for similar texts.

        Args:
            namespace: The namespace to query.
            request: A QueryText object containing the query details.

        Returns:
            A QueryResponse object containing the matched texts and their scores.
        """
        response = await self.client.put(f"/vector/{namespace}", json=request)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryResponse(**data)

    async def delete(self, *, namespace: str, ids: tp.List[str]) -> DeleteResponse:
        """
        Delete embeddings from the vector store by their IDs.

        Args:
            namespace: The namespace to delete embeddings from.
            ids: A list of IDs to delete.

        Returns:
            A DeleteResponse object with the count and IDs of the deleted embeddings.
        """
        response = await self.client.delete(
            f"/vector/{namespace}", params={"ids": ids}
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return DeleteResponse(**data)
