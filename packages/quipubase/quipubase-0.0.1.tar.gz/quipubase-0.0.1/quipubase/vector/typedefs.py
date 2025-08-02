# quipubase/vector/typedefs.py
#
# Pydantic models for Quipubase vector search API requests and responses.

from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from pydantic import BaseModel as Base
from pydantic import Field


# Reusing the BaseModel from the previous example for consistent serialization
class BaseModel(Base):
    """Base model with custom serialization"""

    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


class EmbedText(tpe.TypedDict):
    """Model for upserting texts into the vector store."""

    input: tp.List[str]
    model: tpe.Literal["gemini-embedding-001"]


class QueryText(tpe.TypedDict):
    """Model for querying the vector store."""

    input: str
    top_k: int
    model: tpe.Literal["gemini-embedding-001"]


class UpsertItem(tpe.TypedDict):
    """Model for a single upsert item."""

    id: str
    content: str


class QueryItem(UpsertItem):
    """Model for a single query item."""

    score: float


class UpsertResponse(BaseModel):
    """Model for the response after an upsert operation."""

    count: int = Field(..., description="The number of embeddings that were upserted.")
    ellapsed: float = Field(
        ..., description="The time taken for the upsert in seconds."
    )
    data: tp.List[UpsertItem] = Field(..., description="List of upserted embeddings.")


class QueryResponse(BaseModel):
    """Model for the response from a query operation."""

    data: tp.List[QueryItem] = Field(
        ..., description="List of matched texts and their similarity scores."
    )
    count: int = Field(..., description="The total number of matches found.")
    ellapsed: float = Field(..., description="The time taken for the query in seconds.")


class DeleteResponse(BaseModel):
    """Model for the response after a delete operation."""

    data: tp.List[str] = Field(..., description="List of deleted IDs.")
    count: int = Field(..., description="The number of embeddings that were deleted.")
    ellapsed: float = Field(
        ..., description="The time taken for the delete in seconds."
    )
