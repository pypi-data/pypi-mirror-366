import typing as tp

from httpx import AsyncClient, Response
from loguru import logger

from .typedefs import CollectionDeleteModel, CollectionModel, JSONSchema


class Collections(tp.NamedTuple):
    """Asynchronous client for Quipubase collection endpoints."""
    client: AsyncClient

    async def request(
        self, method: tp.Literal["GET", "POST", "DELETE"], url: str, **kwargs: tp.Any
    ) -> Response:
        return await self.client.request(method, url, **kwargs)

    async def create_collection(self, json_schema: JSONSchema) -> CollectionModel:
        """
        Create a new collection.

        Args:
            json_schema: The JSON schema for the collection.

        Returns:
            A CollectionModel object.
        """
        response = await self.request("POST", "/collections", json=json_schema)
        logger.info(response)
        data = response.json()
        return CollectionModel(**data)

    async def retrieve_collection(self, collection_id: str) -> CollectionModel:
        """
        Retrieve a collection by ID.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            A CollectionModel object.
        """
        response = await self.request("GET", f"/collections/{collection_id}")
        logger.info(response)
        data = response.json()
        return CollectionModel(**data)

    async def delete_collection(self, collection_id: str) -> CollectionDeleteModel:
        """
        Delete a collection by ID.

        Args:
            collection_id: The ID of the collection to delete.

        Returns:
            A CollectionDeleteModel object.
        """
        response = await self.request("DELETE", f"/collections/{collection_id}")
        logger.info(response)
        data = response.json()
        return CollectionDeleteModel(**data)

    async def list_collections(self) -> tp.List[CollectionModel]:
        """
        List all collections.

        Returns:
            A list of CollectionModel objects.
        """
        response = await self.request("GET", "/collections")
        logger.info(response)
        data = response.json()
        return [CollectionModel(**item) for item in data]
