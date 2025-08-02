from openai import AsyncOpenAI

from .blobs import Blobs
from .collections import Collections
from .objects import Objects
from .query import Query
from .vector import Vectors

__all__ = ["Collections", "Objects", "Vectors", "Query", "Blobs", "Quipubase"]


class Quipubase(AsyncOpenAI):
    """Quipubase client"""
    def __init__(self, *, base_url:str="https://quipubase.oscarbahamonde.com/v1",api_key:str="[DEFAULT]",timeout:int=86400):
        super().__init__(base_url=base_url,api_key=api_key,timeout=timeout)

    @property
    def collections(self):
        """
        Collections endpoint of Quipubase
        """
        return Collections(client=self._client)

    @property
    def objects(self):
        """
        Objects endpoint of Quipubase
        """
        return Objects(client=self._client)
    @property
    def query(self):
        """
        Live Query Resource
        """
        return Query(client=self._client)

    @property
    def vector(self):
        """
        Vector Resource
        """
        return Vectors(client=self._client)

    @property
    def blobs(self):
        """
        Blobs
        """
        return Blobs(client=self._client)
