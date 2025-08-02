from __future__ import annotations

import typing as tp

from httpx import AsyncClient
from loguru import logger

from .typedefs import (Adapter, DatasetMetadataResponse,
                       DeleteQueryDatasetResponse, JsonSchemaModel,
                       LiveQueryDatasetMetadata, LiveQueryDatasetQuery,
                       LiveQueryDatasetUpdate, QueryLiveResponse)


class Query(tp.NamedTuple):
    """Asynchronous client for Quipubase query endpoints."""

    client: AsyncClient

    async def list(
        self,
        namespace: str = "default",
        bucket: str = "quipu-store",
    ) -> tp.List[DatasetMetadataResponse]:
        """
        Get a list of datasets.

        Args:
            namespace: The namespace to filter datasets by.
            bucket: The bucket to filter datasets by.

        Returns:
            A list of DatasetMetadataResponse objects.
        """
        params = {"namespace": namespace, "bucket": bucket}
        response = await self.client.get("/query/live", params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return [DatasetMetadataResponse(**d) for d in data]

    async def create(self, request: Adapter) -> QueryLiveResponse:
        """
        Create a new live query dataset.

        Args:
            request: A request object defining the dataset source (File, Mongo, or Postgres).

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.post("/query/live", json=request)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def retrieve(self, request: LiveQueryDatasetQuery) -> QueryLiveResponse:
        """
        Get the data of a specific dataset.

        Args:
            request: A LiveQueryDatasetQuery object.

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.put("/query/live", json=request)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def update(
        self, request: LiveQueryDatasetUpdate
    ) -> QueryLiveResponse:
        """
        Update the data of a specific dataset.

        Args:
            request: A LiveQueryDatasetUpdate object.

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.patch("/query/live", json=request)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def delete(
        self,
        key: str,
        bucket: str = "quipu-store",
        namespace: str = "default",
    ) -> DeleteQueryDatasetResponse:
        """
        Delete a live query dataset.

        Args:
            key: The key of the dataset to delete.
            bucket: The bucket of the dataset to delete.
            namespace: The namespace of the dataset to delete.

        Returns:
            A DeleteQueryDatasetResponse object indicating success.
        """
        response = await self.client.delete(
            "/query/live",
            params={"key": key, "bucket": bucket, "namespace": namespace},
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return DeleteQueryDatasetResponse(**data)

    async def describe(self, request: LiveQueryDatasetMetadata) -> JsonSchemaModel:
        """
        Get the JSON schema of a dataset.

        Args:
            request: A LiveQueryDatasetMetadata object.

        Returns:
            A JsonSchemaModel object containing the dataset's schema.
        """
        response = await self.client.post("/query/schema", json=request)
        response.raise_for_status() 
        data = response.json()
        logger.info(data)
        return JsonSchemaModel(**data)
