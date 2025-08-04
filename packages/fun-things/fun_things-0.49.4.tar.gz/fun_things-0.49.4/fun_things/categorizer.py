from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Tuple,
    TypeVar,
)

T = TypeVar("T")


class Categorizer(Generic[T]):
    def __init__(
        self,
        values: Iterable[T],
        value_selector: Callable[[T], str],
        delimiter: str,
    ):
        self.__delimiter = delimiter
        self.__raw_values = [*values]
        self.__value_selector = value_selector
        self.__values: Dict[T, str] = {}

    def __keyword_sorting_order(self, keyword: str):
        try:
            # Numbers are less prioritized.
            int(keyword)

            return 1
        except Exception:
            pass

        # The rest are prioritized.
        return 2

    def __sorting_order(self, item: Tuple[str, List[T]]):
        return len(item[1]) * self.__keyword_sorting_order(item[0])

    def __most_relevant_keyword(
        self,
        items: Iterable[T],
        ignored_keywords: List[str],
    ):
        result: Dict[str, List[T]] = {}

        for item in items:
            value = self.__get_value(item)
            keywords = value.split(self.__delimiter)

            for keyword in keywords:
                if keyword in ignored_keywords:
                    continue

                if keyword not in result:
                    result[keyword] = []

                if item not in result[keyword]:
                    result[keyword].append(item)

        if not any(result):
            return "", None

        return max(
            result.items(),
            key=self.__sorting_order,
        )

    def __by_keywords(
        self,
        items: Iterable[T],
        ignored_keywords: List[str],
    ):
        """
        Groups the values by keywords.
        """
        items = [*items]

        while True:
            keyword, sub_items = self.__most_relevant_keyword(
                items,
                ignored_keywords,
            )

            if sub_items is None:
                break

            yield keyword, sub_items

            for item in sub_items:
                if item not in items:
                    continue

                items.remove(item)

        if len(items) > 0:
            yield None, items

    def __categorize(
        self,
        items: List[T],
        ignored_keywords: List[str],
    ):
        by_keywords = self.__by_keywords(
            items,
            ignored_keywords,
        )
        result = {}
        others = []

        for keyword, sub_items in by_keywords:
            if len(sub_items) == 1:
                others.append(sub_items[0])
                continue

            if keyword is None:
                for item in sub_items:
                    others.append(item)

                continue

            value = self.__categorize(
                sub_items,
                [*ignored_keywords, keyword],
            )

            if len(value) == 1:
                sub_keyword, value = next(iter(value.items()))

                if sub_keyword is not None:
                    keyword = f"{keyword}_{sub_keyword}"

            result[keyword] = value

        if len(others) > 0:
            result[None] = others

        return result

    def __get_value(self, key: T):
        if key not in self.__values:
            self.__values[key] = self.__value_selector(key)

        return self.__values[key]

    def run(self):
        return self.__categorize(
            self.__raw_values,
            [],
        )


def categorizer(
    values: Iterable[T],
    value_selector: Callable[[T], str] = lambda v: v,  # type: ignore
    delimiter: str = "_",
):
    return Categorizer(
        values=values,
        value_selector=value_selector,
        delimiter=delimiter,
    ).run()
