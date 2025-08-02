from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from pydantic import BaseModel as Base

JSONSchemaType: tpe.TypeAlias = tp.Literal[
    "object", "array", "string", "number", "integer", "boolean"
]


class BaseModel(Base):
    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


class JSONSchema(tpe.TypedDict, total=False):
    type: tpe.NotRequired[JSONSchemaType]
    properties: tpe.NotRequired[tp.Dict[str, JSONSchema]]
    required: tpe.NotRequired[tp.List[str]]
    title: tpe.NotRequired[str]
    description: tpe.NotRequired[str]


class CollectionModel(BaseModel):
    id: str
    sha: str
    json_schema: str | JSONSchema
    created_at: str
    updated_at: str


class CollectionDeleteModel(BaseModel):
    code: int
