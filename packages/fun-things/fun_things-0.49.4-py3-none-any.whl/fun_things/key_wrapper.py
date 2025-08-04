from dataclasses import dataclass
from typing import Callable, Generic, List, Optional, TypeVar

TItem = TypeVar("TItem")
TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


@dataclass(frozen=True)
class KeyWrapper(Generic[TItem, TKey, TValue]):
    """
    Wrapper made for `bisect`.

    A utility class designed to work with Python's bisect module for maintaining sorted lists.
    It allows custom key and value selectors for more complex sorting and insertion operations.

    Type Parameters:
        TItem: The type of items stored in the wrapped list.
        TKey: The type of keys used for comparison.
        TValue: The type of values used when inserting new items.
    """

    items: List[TItem]
    key_selector: Optional[Callable[[TItem], TKey]] = None
    value_selector: Optional[Callable[[TKey], TValue]] = None

    def __getitem__(self, index):
        item = self.items[index]

        if self.key_selector is None:
            return item

        return self.key_selector(item)

    def __len__(self):
        return len(self.items)

    def insert(self, index, item):
        """
        Insert an item into the wrapped list at the specified index.

        If a value_selector is defined, the item is transformed before insertion.

        Args:
            index: The index at which to insert the item.
            item: The item to insert, or if value_selector is defined, the key to transform into a value.
        """
        if self.value_selector is not None:
            item = self.value_selector(item)

        self.items.insert(index, item)  # type: ignore
