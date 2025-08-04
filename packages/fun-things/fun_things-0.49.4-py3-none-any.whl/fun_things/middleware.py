from abc import ABC
from signal import SIGABRT, SIGCONT, SIGTERM
from typing import (
    Dict,
    Generic,
    List,
    Type,
    TypeVar,
    Union,
    final,
)

import fun_things.logger
from fun_things import as_gen

TParent = TypeVar("TParent", bound="Middleware")
TChild = TypeVar("TChild", bound="Middleware")


class Middleware(Generic[TParent], ABC):
    logger = fun_things.logger.new("Middleware")

    PRIORITY: int = 0
    MIDDLEWARES: List[Type["Middleware"]] = []
    """
    Nested middlewares.
    """
    parent: TParent = None  # type: ignore

    __middleware_instances: Dict[
        Type["Middleware"],
        "Middleware",
    ]
    __all_middleware_instances: Dict[
        Type["Middleware"],
        "Middleware",
    ]

    @property
    def root(self):
        return self.__root

    def get_middleware(
        self,
        type: Union[Type[TChild], str],
        recursive: bool = True,
    ) -> TChild:
        middlewares = self.__middleware_instances

        if recursive:
            middlewares = self.__root.__all_middleware_instances

        if isinstance(type, str):
            for key in middlewares:
                if key.__name__ == type:
                    return middlewares[key]  # type: ignore

            return None  # type: ignore

        return middlewares.get(type)  # type: ignore

    def before_run(self):
        """
        Called before the nested middlewares are called.

        Return `signal.SIGABRT` to stop this middleware.

        Return `signal.SIGTERM` to stop the whole process.
        """
        pass

    def after_run(self):
        """
        Called after the nested middlewares are called.

        Return `signal.SIGABRT` to stop this middleware.

        Return `signal.SIGTERM` to stop the whole process.
        """
        pass

    @final
    def __instantiate(self, middleware: Type[TChild]):
        instance = middleware()
        self.__middleware_instances[middleware] = instance
        self.__root.__all_middleware_instances[middleware] = instance
        instance.parent = self

        return instance

    @final
    def __build_annotations(self):
        if "__annotations__" not in self.__class__.__dict__:
            return

        annotations = self.__class__.__annotations__

        for key, type in annotations.items():
            try:
                if not issubclass(type, Middleware):
                    continue

            except Exception:
                continue

            setattr(self, key, self.__instantiate(type))

    @final
    def run_all(self):
        return [*self.run()]

    @final
    def run(self):
        if self.parent is None:
            self.__all_middleware_instances = {
                self.__class__: self,
            }
            self.__root = self
        else:
            self.__root = self.parent.__root

        self.__middleware_instances = {}

        self.__build_annotations()

        for middleware in self.MIDDLEWARES:
            self.__instantiate(middleware)

        self.logger.debug(
            "{0} {1}".format(
                "BeforeRun",
                self.__class__.__name__,
            )
        )

        for item in as_gen(self.before_run()):
            if item == SIGCONT:
                continue

            if item == SIGABRT:
                return

            if item == SIGTERM:
                if self.parent is not None:
                    yield SIGTERM

                return

        middlewares = sorted(
            self.__middleware_instances.values(),
            key=lambda middleware: middleware.PRIORITY,
            reverse=True,
        )

        for middleware in middlewares:
            for item in middleware.run():
                if item == SIGCONT:
                    continue

                if item == SIGABRT:
                    return

                if item == SIGTERM:
                    if self.parent is not None:
                        yield SIGTERM

                    return

        self.logger.debug(
            "{0} {1}".format(
                "AfterRun",
                self.__class__.__name__,
            )
        )

        for item in as_gen(self.after_run()):
            if item == SIGCONT:
                continue

            if item == SIGABRT:
                return

            if item == SIGTERM:
                if self.parent is not None:
                    yield SIGTERM

                return
