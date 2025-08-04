from typing import Callable, Any, Iterable, TypeVar, Generator
from functools import reduce
from random import random

T = TypeVar("T")


def weighted_distribution(
    items: Iterable[T],
    weight_selector: Callable[[T], float] = lambda v: v,  # type: ignore
) -> Generator[T, Any, None]:
    """
    Choose a random item based on their given weight.

    A higher weight means they have
    a higher chance of being chosen.

    0 or negative weights are ignored.
    """
    weighted_items = []

    for item in items:
        weight = weight_selector(item)

        if weight <= 0:
            continue

        weighted_items.append(
            {
                "item": item,
                "weight": weight,
            }
        )

    weighted_items.sort(key=lambda item: item["weight"])

    max_weight = reduce(
        lambda value, item: value + item["weight"],
        weighted_items,
        0,
    )

    while len(weighted_items) > 0:
        value = random() * max_weight

        for item in weighted_items:
            weight = item["weight"]
            if value < weight:
                yield item["item"]
                break

            value -= weight
