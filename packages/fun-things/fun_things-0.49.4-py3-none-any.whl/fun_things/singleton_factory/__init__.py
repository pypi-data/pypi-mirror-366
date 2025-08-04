from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    final,
)

T = TypeVar("T")


class SingletonFactory(Generic[T], ABC):
    """
    Abstract base class implementing the Singleton-Factory design pattern.

    Ensures that only one instance of a class is created, and provides methods for
    destroying the instance and keeping track of all instances.

    Subclasses must implement the `_instantiate` and `_destroy` abstract methods.
    """

    __all: List["SingletonFactory"] = []

    __instantiated: bool = False
    __instance: T

    __kwargs: Optional[dict] = None
    __kwargs_fn: Optional[Callable[[], dict]] = None

    log: bool = True

    @property
    def instance(self):
        """
        Returns the instance of the Singleton class.

        The instance is created on first invocation and
        remains the same for all subsequent invocations.

        :return: The instance of the Singleton class
        :rtype: T
        """
        return self()

    @property
    def kwargs(self) -> dict:
        if self.__kwargs is None:
            if self.__kwargs_fn is None:
                raise Exception('"kwargs" is not available!')

            self.__kwargs = self.__kwargs_fn()

        return self.__kwargs

    @property
    def args(self):
        return self.__args

    def __init__(self, *args, **kwargs):
        self.__kwargs = kwargs
        self.__args = args

        SingletonFactory.__all.append(self)

    def __call__(self):
        """
        Returns the instance of the Singleton class.

        The instance is created on first invocation and
        remains the same for all subsequent invocations.

        :return: The instance of the Singleton class
        :rtype: T
        """
        if not self.__instantiated:
            self.__instance = self._instantiate()
            self.__instantiated = True

            if self.log:
                print(
                    f"Instantiated '{self.__class__.__name__}'.",
                    self.__instance,
                )

        return self.__instance

    @abstractmethod
    def _instantiate(self) -> T:
        """
        Instantiates the Singleton class.

        This method is called when the instance is first requested.
        It should create and return the instance of the Singleton class.

        :return: The instance of the Singleton class
        :rtype: T
        """
        pass

    @abstractmethod
    def _destroy(self) -> bool:
        """
        Destroys the instance of the Singleton class.

        This method is called when the `destroy` method is invoked.
        It should destroy the instance of the Singleton class and
        return `True` if the destruction was successful.

        :return: `True` if the instance was destroyed.
        :rtype: bool
        """
        pass

    @final
    def destroy(self):
        """
        Destroys the instance of the Singleton class.

        :return: `True` if the instance was destroyed.
        :rtype: bool
        """
        if not self.__instantiated:
            return False

        ok = self._destroy()

        if ok:
            self.__instantiated = False

            if self.log:
                print(
                    f"Destroyed '{self.__class__.__name__}'.",
                    self.__instance,
                )

        return ok

    @final
    @classmethod
    def new(cls, fn: Callable[[], Dict[str, Any]]):
        """
        Creates a new instance of the Singleton class
        using a callable function as the configuration provider.

        The callable is expected to return a dictionary
        containing the configuration to be passed to the constructor.

        :param fn: A callable returning a dictionary
        :type fn: Callable[[], Dict[str, Any]]
        :return: The new instance of the Singleton class
        :rtype: T
        """
        singleton = cls()
        singleton.__kwargs = None
        singleton.__kwargs_fn = fn

        return singleton

    @final
    @classmethod
    def all(cls):
        """
        Yields all instances of the Singleton class.

        This method is a generator function which yields all instances
        of the Singleton class. The order in which the instances are
        returned is not guaranteed.

        :return: A generator of all instances of the Singleton class
        :rtype: Iterator[T]
        """
        for instance in cls.__all:
            yield instance

    @final
    @classmethod
    def destroy_all(cls):
        """
        Destroys all instances of the Singleton class.

        Iterates over all stored instances and calls their `destroy` method.
        Returns the count of instances that were successfully destroyed.

        :return: The number of instances destroyed
        :rtype: int
        """
        n = 0

        for conn in cls.__all:
            if conn.destroy():
                n += 1

        return n
