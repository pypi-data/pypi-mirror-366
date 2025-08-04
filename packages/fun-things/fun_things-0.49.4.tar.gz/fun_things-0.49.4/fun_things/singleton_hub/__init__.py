from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, final

T = TypeVar("T")


class Catcher(Generic[T]):
    """
    A context manager for handling errors in singleton hub operations.

    This class provides a context manager interface for handling errors that may
    occur during singleton hub operations. It allows for automatic error handling,
    optional clearing of values on error, and control over whether errors are
    re-raised.

    :param hub: The singleton hub instance
    :param name: The name of the value being accessed
    :param value: The value being accessed
    :param clear_on_error: Whether to clear the value from cache on error
    :param raise_error: Whether to re-raise the error after handling
    """

    def __init__(
        self,
        hub: "SingletonHubMeta[T]",
        name: str,
        value: T,
        clear_on_error: bool,
        raise_error: bool,
    ):
        self.hub = hub
        self.name = name
        self.value = value
        self.clear_on_error = clear_on_error
        self.raise_error = raise_error

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.hub._on_error(
                self.name,
                self.value,
                exc_value,
            )

            if self.clear_on_error:
                self.hub.clear(self.name)

            return not self.raise_error


class SingletonHubMeta(ABC, type, Generic[T]):
    @property
    def __key_cache(cls) -> Dict[str, str]:
        return cls.__get("__key_cache", {})

    @property
    def __value_cache(cls) -> Dict[str, T]:
        return cls.__get("__value_cache", {})

    def __get(cls, key: str, default):
        if not hasattr(cls, key):
            setattr(cls, key, default)

        return getattr(cls, key)

    def _name_selector(cls, name: str):
        return name

    @abstractmethod
    def _value_selector(cls, name: str) -> T:
        pass

    def _on_error(
        cls,
        key: str,
        value: T,
        e: Exception,
    ) -> None:
        pass

    def _on_clear(cls, key: str, value: T) -> None:
        pass

    @final
    def clear(cls, name: str):
        """
        Clear the cached value associated with the given name.

        This method first checks if the name exists in the key cache. If it
        does, it retrieves the corresponding key. If not, it returns a tuple
        of `(None, None)`.

        Then, it checks if the key exists in the value cache. If it does, it
        retrieves the corresponding value, calls the `_on_clear` method with
        the key and value, and then removes the key from the value cache. If
        not, it returns a tuple of `(key, None)`.

        :param name: The name used to retrieve or create the value.
        :return: A tuple of `(key, value)` where `value` is the cleared value
            associated with the given name, or `(key, None)` if the key does
            not exist in the value cache.
        """
        if name not in cls.__key_cache:
            return None, None

        key = cls.__key_cache[name]

        if key not in cls.__value_cache:
            return key, None

        value = cls.__value_cache[key]

        cls._on_clear(key, value)

        del cls.__value_cache[key]

        return key, value

    @final
    def clear_all(cls):
        """
        Clear all cached values and return them in a dictionary.

        :return: A dictionary mapping key names to the cleared values
        :rtype: Dict[str, T]
        """
        result: Dict[str, T] = {}

        for key, value in cls.__value_cache.items():
            result[key] = value

            cls._on_clear(key, value)

        cls.__value_cache.clear()

        return result

    @final
    def get(
        cls,
        name: str = "",
    ):
        """
        Retrieve or create a value associated with the given name.

        This method first checks if the name exists in the key cache. If it
        does, it retrieves the corresponding key. If not, it generates a key
        using the `_name_selector` method and caches it. Then, it checks if
        the key exists in the value cache. If it does, it returns the
        corresponding value. If not, it creates the value using the
        `_value_selector` method, caches it, and returns it.

        :param name: The name used to retrieve or create the value.
        :return: The value associated with the given name.
        """

        if name in cls.__key_cache:
            key = cls.__key_cache[name]
        else:
            key = cls.__key_cache[name] = cls._name_selector(name)

        if key in cls.__value_cache:
            return cls.__value_cache[key]

        value = cls.__value_cache[key] = cls._value_selector(key)

        return value

    @final
    def catch(
        cls,
        name: str = "",
        *,
        clear_on_error: bool = True,
        raise_error: bool = False,
    ):
        """
        Create a context manager for handling errors in singleton hub operations.

        This method creates a context manager that wraps the value retrieved from
        the singleton hub. It provides error handling capabilities and control over
        whether values are cleared from cache on error.

        :param name: The name used to retrieve the value.
        :param clear_on_error: Whether to clear the value from cache on error.
        :param raise_error: Whether to re-raise the error after handling.
        :return: A context manager for the retrieved value.
        """
        return Catcher(
            cls,
            name,
            cls.get(name),
            clear_on_error,
            raise_error,
        )

    def __getattr__(cls, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)

        return cls.get(name)
