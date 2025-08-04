from typing import List, Optional

from fastapi_healthz import (
    HealthCheckAbstract,
)
from fastapi_healthz.models import HealthCheckStatusEnum
from redis import Redis


class HealthCheckRedis2(HealthCheckAbstract):
    def __init__(
        self,
        host: str,
        port: int,
        password: Optional[str] = None,
        service: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(service, tags)

        self.__host = host
        self.__port = port
        self.__password = password
        self.__kwargs = kwargs

    @property
    def service(self) -> str:
        return self._service if self._service is not None else "redis"

    @property
    def connection_uri(self) -> Optional[str]:
        return f"redis://{self.__password + '@' if self.__password else ''}{self.__host}:{self.__port}"

    def check_health(self) -> HealthCheckStatusEnum:
        try:
            redis = Redis(
                host=self.__host,
                port=self.__port,
                password=self.__password,
                **self.__kwargs,
            )

            ok = redis.ping()

            return (
                HealthCheckStatusEnum.HEALTHY if ok else HealthCheckStatusEnum.UNHEALTHY
            )

        except Exception:
            return HealthCheckStatusEnum.UNHEALTHY
