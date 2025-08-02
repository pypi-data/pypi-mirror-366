# quipubase/files/client.py
#
# Asynchronous client for Quipubase file endpoints.

from __future__ import annotations

import json
import typing as tp

from httpx import AsyncClient

from .typedefs import (ChunkFile, DeleteFile, FileType, GetOrCreateFile,
                       RequestFiles)


class Blobs(tp.NamedTuple):
    """Asynchronous client for Quipubase file endpoints."""

    client: AsyncClient

    async def chunk_file(
        self, files: RequestFiles, format: tp.Literal["html", "text"]
    ) -> ChunkFile:
        """
        Uploads a file and chunks it.

        Args:
            files: The file data to upload.
            format: The format of the file, "html" or "text".

        Returns:
            A ChunkFile object with a success message and file ID.
        """
        params: tp.Dict[str, tp.Any] = {"format": format}
        response = await self.client.post("/blob", params=params, files=files)
        response.raise_for_status()
        return ChunkFile(**response.json())

    async def get_or_create_file(
        self, path: str, files: tp.Any, bucket: tp.Optional[str] = None
    ) -> GetOrCreateFile:
        """
        Uploads a file and creates a new one at the specified path.

        Args:
            path: The path of the file.
            files: The file data to upload.
            bucket: The bucket to store the file in.

        Returns:
            A GetOrCreateFile object.
        """
        params: tp.Dict[str, tp.Any] = {}
        if bucket:
            params["bucket"] = bucket
        response = await self.client.put(
            f"/blob/{path}", params=params, files=files
        )
        response.raise_for_status()
        return GetOrCreateFile(**response.json())

    async def delete_file(
        self, path: str, bucket: tp.Optional[str] = None
    ) -> DeleteFile:
        """
        Deletes a file at the specified path.

        Args:
            path: The path of the file to delete.
            bucket: The bucket the file is in.

        Returns:
            A DeleteFile object indicating success.
        """
        params: tp.Dict[str, tp.Any] = {}
        if bucket:
            params["bucket"] = bucket
        response = await self.client.delete(f"/blob/{path}", params=params)
        response.raise_for_status()
        return DeleteFile(**response.json())

    async def get_file(
        self, path: str, bucket: tp.Optional[str] = None
    ) -> GetOrCreateFile:
        """
        Gets a file at the specified path.

        Args:
            path: The path of the file.
            bucket: The bucket the file is in.

        Returns:
            A GetOrCreateFile object.
        """
        params: tp.Dict[str, tp.Any] = {}
        if bucket:
            params["bucket"] = bucket
        response = await self.client.get(f"/blob/{path}", params=params)
        response.raise_for_status()
        return GetOrCreateFile(**response.json())

    async def get_file_tree(self, path: str, bucket: tp.Optional[str] = None) -> tp.Any:
        """
        Gets the file tree for a given path.

        Args:
            path: The path to get the file tree from.
            bucket: The bucket to look in.

        Returns:
            The raw JSON data of the file tree.
        """
        params: tp.Dict[str, tp.Any] = {}
        if bucket:
            params["bucket"] = bucket
        async with self.client.stream(
            "GET", f"/blobs/{path}", params=params
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_lines():
                data = chunk[6:]
                yield FileType(**json.loads(data))
