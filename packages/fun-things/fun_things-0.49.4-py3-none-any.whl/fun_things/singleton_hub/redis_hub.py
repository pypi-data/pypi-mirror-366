import os

from redis import Redis

from .environment_hub import EnvironmentHubMeta


class RedisHubMeta(EnvironmentHubMeta[Redis]):
    _formats = EnvironmentHubMeta._bake_basic_uri_formats(
        "REDIS",
    )
    _kwargs: dict = {}
    _log: bool = True

    def _value_selector(cls, name: str):
        client = Redis.from_url(
            os.environ.get(name) or "",
            **cls._kwargs,
        )

        if cls._log:
            print(f"Redis `{name}` instantiated.")

        return client

    def _on_clear(
        cls,
        key: str,
        value: Redis,
    ) -> None:
        value.close()

        if cls._log:
            print(f"Redis `{key}` closed.")


class RedisHub(metaclass=RedisHubMeta):
    def __new__(cls, name: str = ""):
        return cls.get(name)
