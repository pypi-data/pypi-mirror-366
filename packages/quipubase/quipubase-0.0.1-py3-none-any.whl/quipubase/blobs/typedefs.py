# quipubase/files/typedefs.py
#
# Pydantic models for Quipubase Files API responses.

from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from pydantic import BaseModel as Base

FileContent = tp.Union[tp.IO[bytes], bytes, str]
FileTypes: tpe.TypeAlias = tp.Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    tp.Tuple[tp.Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    tp.Tuple[tp.Optional[str], FileContent, tp.Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    tp.Tuple[tp.Optional[str], FileContent, tp.Optional[str], tp.Mapping[str, str]],
]
RequestFiles: tpe.TypeAlias = tp.Union[
    tp.Mapping[str, FileTypes], tp.Sequence[tp.Tuple[str, FileTypes]]
]


class BaseModel(Base):
    """Base model with custom serialization"""

    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


# --- Files API Response Models ---
class ChunkFile(BaseModel):
    chunks: list[str]
    created: float
    chunkedCount: int


class FileType(BaseModel):
    url: str
    path: str


class GetOrCreateFile(BaseModel):
    data: FileType
    created: float


class DeleteFile(BaseModel):
    deleted: bool


class TreeNode(BaseModel):
    type: tp.Literal["file", "folder"]
    name: str
    path: str
    content: str | list[TreeNode]
