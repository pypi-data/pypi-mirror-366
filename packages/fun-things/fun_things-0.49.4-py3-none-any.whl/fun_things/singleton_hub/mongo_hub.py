import os

from pymongo import MongoClient

from .environment_hub import EnvironmentHubMeta


class MongoHubMeta(EnvironmentHubMeta[MongoClient]):
    _formats = EnvironmentHubMeta._bake_basic_uri_formats(
        "MONGO",
        "MONGO_DB",
        "MONGODB",
    )
    _kwargs: dict = {}
    _log: bool = True

    def _value_selector(cls, name: str):
        client = MongoClient(
            os.environ.get(name),
            **cls._kwargs,
        )

        if cls._log:
            print(f"MongoDB `{name}` instantiated.")

        return client

    def _on_clear(
        cls,
        key: str,
        value: MongoClient,
    ) -> None:
        value.close()

        if cls._log:
            print(f"MongoDB `{key}` closed.")


class MongoHub(metaclass=MongoHubMeta):
    def __new__(cls, name: str = ""):
        return cls.get(name)
