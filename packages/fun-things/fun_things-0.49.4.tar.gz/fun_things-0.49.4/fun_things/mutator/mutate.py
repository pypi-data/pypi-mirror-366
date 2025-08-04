from typing import List, Union
from .mutator import Mutator


def mutate(
    obj: object,
    *method_names: Union[str, List[str]],
    mutation_key="!mutator",
):
    """
    Mutate the given method names.

    These methods are wrapped.
    """
    if not hasattr(obj, mutation_key):
        setattr(
            obj,
            mutation_key,
            [
                set(),  # wrapped
                {},  # replacers
                {},  # prefixes
                {},  # postfixes
            ],
        )

    mutation = getattr(obj, mutation_key)
    flat_names = []

    for name in method_names:
        if isinstance(name, str):
            flat_names.append(name)
        else:
            for name0 in name:
                flat_names.append(name0)

    return Mutator(
        obj,
        flat_names,
        mutation[0],
        mutation[1],
        mutation[2],
        mutation[3],
    )
