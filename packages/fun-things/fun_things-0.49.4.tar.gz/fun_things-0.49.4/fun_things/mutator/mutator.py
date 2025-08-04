from typing import Callable, Dict, List, Set, Union
from .affix import Affix
from .postfix import Postfix
from .prefix import Prefix
from ..key_wrapper import KeyWrapper
import bisect


class Mutator:
    def __init__(
        self,
        obj: object,
        names: List[str],
        wrapped: Set[str],
        replacers: Dict[str, Callable],
        prefixes: Dict[str, List[Affix]],
        postfixes: Dict[str, List[Affix]],
    ):
        self.__obj = obj
        self.__names = names
        self.__wrapped = wrapped
        self.__replacers = replacers
        self.__prefixes = prefixes
        self.__postfixes = postfixes

        for name in names:
            if name not in self.__wrapped:
                self.__wrapped.add(name)
                self.__wrap(name)

    def __wrap(self, name: str):
        raw = getattr(self.__obj, name)

        def wrapper(*args, **kwargs):
            prefix_payload = Prefix(
                args=list(args),
                kwargs=kwargs,
                proceed=True,
            )

            if name in self.__prefixes:
                for hook in self.__prefixes[name]:
                    hook.fn(prefix_payload)

            if not prefix_payload.proceed:
                return prefix_payload.return_value

            value = None

            if name in self.__replacers:
                value = self.__replacers[name](
                    *prefix_payload.args,
                    **prefix_payload.kwargs,
                )
            else:
                value = raw(
                    *prefix_payload.args,
                    **prefix_payload.kwargs,
                )

            postfix_payload = Postfix(
                args=prefix_payload.args,
                kwargs=prefix_payload.kwargs,
                return_value=value,
            )

            if name in self.__postfixes:
                for hook in self.__postfixes[name]:
                    hook.fn(postfix_payload)

            return value

        setattr(self.__obj, name, wrapper)

    def prefix(
        self,
        fn: Callable[[Prefix], None],
        priority: int = 0,
    ):
        for name in self.__names:
            if name not in self.__prefixes:
                self.__prefixes[name] = []

            bisect.insort_right(
                KeyWrapper(
                    items=self.__prefixes[name],
                    key_selector=lambda item: item.priority,
                    value_selector=lambda _: Affix(
                        priority=priority,
                        fn=fn,
                    ),
                ),  # type: ignore
                priority,
            )

        return self

    def postfix(
        self,
        fn: Callable[[Postfix], None],
        priority: int = 0,
    ):
        for name in self.__names:
            if name not in self.__postfixes:
                self.__postfixes[name] = []

            bisect.insort_right(
                KeyWrapper(
                    items=self.__postfixes[name],
                    key_selector=lambda item: item.priority,
                    value_selector=lambda _: Affix(
                        priority=priority,
                        fn=fn,
                    ),
                ),  # type: ignore
                priority,
            )

        return self

    def replace(self, replacer: Union[Callable, object]):
        """
        Replaces the corresponding methods
        with the given callable,
        or the object's method with the same name.
        """
        is_callable = callable(replacer)

        for name in self.__names:
            if is_callable:
                self.__replacers[name] = replacer
            else:
                self.__replacers[name] = getattr(replacer, name)

        return self

    def remove_postfix(self, fn: Callable):
        """
        Removes all occurrences of the given function.
        """
        for name in self.__names:
            if name not in self.__postfixes:
                continue

            self.__postfixes[name] = list(
                filter(
                    lambda affix: affix.fn == fn,
                    self.__postfixes[name],
                )
            )

        return self

    def remove_prefix(self, fn: Callable):
        """
        Removes all occurrences of the given function.
        """
        for name in self.__names:
            if name not in self.__prefixes:
                continue

            self.__prefixes[name] = list(
                filter(
                    lambda affix: affix.fn == fn,
                    self.__prefixes[name],
                )
            )

        return self

    def remove_replacer(self):
        """
        Remove replacers from these methods.
        """
        for name in self.__names:
            if name in self.__replacers:
                del self.__replacers[name]

        return self
