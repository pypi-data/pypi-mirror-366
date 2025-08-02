# quipubase/objects/typedefs.py

from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from pydantic import BaseModel as Base
from pydantic import Field

QuipuActions: tpe.TypeAlias = tp.Literal[
    "create", "read", "update", "delete", "query", "stop"
]


class BaseModel(Base):
    """Base model"""

    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


class SubResponse(BaseModel):
    """Event model"""

    event: QuipuActions
    data: dict[str, tp.Any] | list[dict[str, tp.Any]]


class PubResponse(BaseModel):
    """Response model"""

    collection: str
    data: dict[str, tp.Any] | list[dict[str, tp.Any]]
    event: QuipuActions


class QuipubaseRequest(BaseModel):
    """
    Quipubase Request
    A model representing a request to the Quipubase API. This model includes fields for the action type, record ID, and any additional data required for the request.
    Attributes:
            event (QuipuActions): The action to be performed (create, read, update, delete, query).
            id (Optional[str]): The unique identifier for the record. If None, a new record will be created.
            data (Optional[Dict[str, Any]]): Additional data required for the request. This can include fields to update or query parameters.
    """

    model_config = {
        "extra": "ignore",
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "event": "create",
                "id": None,
                "data": {
                    "title": "Example Record",
                    "description": "This is an example record for testing purposes.",
                    "done": False,
                },
            }
        },
    }
    event: QuipuActions = Field(default="query")
    id: tp.Optional[str] = Field(default=None)
    data: tp.Optional[tp.Dict[str, tp.Any]] = Field(
        default=None,
        description="The `data` property of the request body is an object that is of the type documented on the `collection_id`",
    )
