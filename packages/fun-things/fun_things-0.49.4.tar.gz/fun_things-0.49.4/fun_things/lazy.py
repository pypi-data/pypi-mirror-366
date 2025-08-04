from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
TValue = TypeVar("TValue", bound=Callable)


class lazy(Generic[T]):
    """
    A lazy initialization attribute.
    
    This class implements the descriptor protocol for lazy loading of attributes.
    It delays the computation of a value until it is actually needed.
    """

    def __init__(
        self,
        fn: Callable[..., T],
    ) -> None:
        """
        Initialize a lazy attribute.
        
        Args:
            fn (Callable[..., T]): The function to call when the value is first accessed.
                                   This function will compute the actual value.
        """
        self.__fn = fn
        self.__instance: T = None  # type: ignore
        self.__exists: bool = False

    def __get__(self, instance, cls) -> T:
        if instance is None:
            return self  # type: ignore

        value = self.__fn(instance)

        setattr(
            instance,
            self.__fn.__name__,
            value,
        )

        return value

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> T:
        if not self.__exists:
            self.__exists = True
            self.__instance = self.__fn(
                *args,
                **kwargs,
            )

        return self.__instance

    @property
    def self(self):
        """
        Get the cached instance value.
        
        Returns:
            T: The cached value.
            
        Raises:
            Exception: If the value hasn't been initialized yet.
        """
        if not self.__exists:
            raise Exception("The instance is not initialized!")

        return self.__instance

    @property
    def exists(self):
        """
        Check if the value has been initialized.
        
        Returns:
            bool: True if the value has been computed, False otherwise.
        """
        return self.__exists

    def clear(self):
        """
        Clears the initialized value.
        
        Resets the lazy attribute so that the next access will
        recompute the value.
        """
        self.__exists = False
        self.__instance = None  # type: ignore

    @staticmethod
    def fn(fn: TValue) -> TValue:
        """
        A static method that transforms a given callable into a memoized version.

        The returned callable caches the result of the first invocation and returns
        the cached result on subsequent calls, regardless of the input arguments.

        :param fn: The original function to be memoized.
        :return: A memoized version of the original function.
        """
        _value = []

        def wrapper(*args, **kwargs) -> Any:
            if not _value:
                _value.append(fn(*args, **kwargs))

            return _value[0]

        return wrapper  # type: ignore
