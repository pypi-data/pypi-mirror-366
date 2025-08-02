# Pydantic models for Quipubase vector search API requests and responses.

from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from pydantic import BaseModel as Base


# Reusing the BaseModel from the previous example for consistent serialization
class BaseModel(Base):
    """Base model with custom serialization"""

    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


class LiveQueryDatasetMetadata(tpe.TypedDict):
    """Metadata for a live query dataset."""

    key: str
    bucket: tpe.NotRequired[str]
    namespace: tpe.NotRequired[str]


class LiveQueryDatasetQuery(LiveQueryDatasetMetadata):
    """Request model for querying a live dataset."""

    query: str


class LiveQueryDatasetUpdate(LiveQueryDatasetMetadata):
    """Request model for updating a live dataset."""

    data: tp.List[tp.Dict[str, tp.Any]]


class Adapter(tpe.TypedDict):
    """Request model for creating a file-based dataset."""

    engine: tp.Literal["file", "mongodb", "postgresql"]
    uri: str
    query: str
    key: tpe.NotRequired[str]
    namespace: tpe.NotRequired[str]
    bucket: tpe.NotRequired[str]


# --- Query API Response Models ---


class DatasetMetadataResponse(BaseModel):
    """Response model for dataset metadata."""

    key: str
    bucket: str
    namespace: str


class QueryLiveResponse(BaseModel):
    """Response model for live query operations (PUT, PATCH)."""

    data: tp.List[tp.Dict[str, tp.Any]]
    json_schema: tp.Dict[str, tp.Any]
    key: str


class DeleteQueryDatasetResponse(BaseModel):
    """Response model for deleting a live query dataset."""

    success: bool


class JsonSchemaModel(tpe.TypedDict):
    """Response model for getting a dataset's JSON schema."""

    ...
