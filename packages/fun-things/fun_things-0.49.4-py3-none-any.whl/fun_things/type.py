from typing import Any, Generator, Iterable, Type, TypeVar

T = TypeVar("T", bound=Type)


def get_all_descendant_classes(
    cls: T,
    exclude: Iterable[Type] = (),
) -> Generator[T, Any, None]:
    """
    Returns all direct and indirect subclasses of a given class.
    
    This function performs a breadth-first search to find all classes that inherit
    from the specified class, directly or indirectly through the inheritance tree.
    
    Args:
        cls (Type): The base class to find descendants of.
        exclude (Iterable[Type], optional): Collection of classes to exclude from the results.
                                           Note that subclasses of excluded classes will still
                                           be included unless they also directly inherit from
                                           an excluded class. Defaults to an empty tuple.
    
    Returns:
        Generator[T, Any, None]: A generator yielding all descendant classes of the specified class,
                                except those that directly inherit from classes in the exclude list.
    
    Examples:
        >>> list(get_all_descendant_classes(BaseClass))
        [SubClass1, SubClass2, SubClass1Child, ...]
        
        >>> list(get_all_descendant_classes(BaseClass, exclude=[SubClass1]))
        [SubClass2, ...]  # SubClass1Child is still included if it doesn't directly inherit from SubClass1
    """
    queue = [cls]
    subclasses = cls.__subclasses__()

    while len(queue) > 0:
        subclasses = queue.pop().__subclasses__()

        for subclass in subclasses:
            intersection = set(exclude) & set(subclass.__bases__)

            if not intersection:
                yield subclass

            queue.append(subclass)
