import httpx
from .collections import Collections
from .objects import Objects
from .query import Query
from .vector import Vectors
from .blobs import Blobs
from openai import AsyncOpenAI

__all__ = ["Collections", "Objects", "Vectors", "Query", "Blobs", "Quipubase"]

class Quipubase(AsyncOpenAI):
	"""Quipubase client"""
	@property
	def collections(self) -> Collections:
		return Collections(client=self._client)

	@property
	def objects(self) -> Objects:
		return Objects(client=httpx.AsyncClient(base_url=self.base_url,timeout=86400))

	@property
	def query(self) -> Query:
		return Query(client=self._client)

	@property
	def vector(self) -> Vectors:
		return Vectors(client=self._client)

	@property
	def blobs(self) -> Blobs:
		return Blobs(client=httpx.AsyncClient(base_url=self.base_url,timeout=86400))