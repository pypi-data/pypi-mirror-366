import os
from importlib import import_module
from pkgutil import iter_modules


def merge_dict(
    *dicts: dict,
    **kwargs,
):
    """
    Merge multiple dictionaries into a single dictionary.

    Args:
        *dicts: Variable number of dictionaries to merge.
        **kwargs: Additional key-value pairs to include in the merged dictionary.

    Returns:
        dict: A new dictionary containing all key-value pairs from all input dictionaries.
              If keys conflict, later dictionaries will override earlier ones.

    Examples:
        >>> merge_dict({'a': 1}, {'b': 2}, c=3)
        {'a': 1, 'b': 2, 'c': 3}
    """
    result = {}

    for dict in dicts:
        result.update(dict)

    result.update(kwargs)

    return result


def load_modules(
    path: str,
    recursive: bool = True,
):
    """
    Load Python modules from a specified path.

    Args:
        path (str): The import path to load modules from (e.g., 'package.subpackage').
        recursive (bool, optional): Whether to recursively load modules from subfolders.
                                   Defaults to True.

    Yields:
        module: Each loaded module object.

    Examples:
        >>> # Load all modules from a package
        >>> for module in load_modules('fun_things'):
        ...     print(module.__name__)

        >>> # Load only direct modules (non-recursive)
        >>> for module in load_modules('fun_things', recursive=False):
        ...     print(module.__name__)
    """
    mod = import_module(path)

    yield mod

    if not hasattr(mod, "__path__"):
        return

    for _, subpath, ispkg in iter_modules(mod.__path__):
        full_path = path + "." + subpath

        if ispkg:
            # Package (subfolder with __init__.py.)
            yield from load_modules(full_path)
            continue

        # Regular module.
        submod = import_module(full_path)

        yield submod

    if not recursive:
        return

    folder_path = path.replace(".", "/")

    for name in os.listdir(folder_path):
        if name.startswith("__") and name.endswith("__"):
            continue

        if not os.path.isdir(os.path.join(folder_path, name)):
            continue

        yield from load_modules(f"{path}.{name}")
