from dataclasses import dataclass
import re
from typing import Dict, List, Optional
import boolean
from boolean.boolean import BooleanAlgebra


class BooleanQuery:
    """
    Represents a boolean query that can be evaluated against a given text.

    The query is parsed from a string and can contain keywords, phrases, and logical operators.
    The query is then evaluated against a text using regular expressions, and the result is a boolean indicating whether the query matches the text.

    This class provides a way to construct and evaluate complex boolean queries in a flexible and efficient manner.
    It is designed to be used in a variety of applications, including search engines, data filtering, and text analysis.
    """

    @dataclass(frozen=True)
    class Value:
        key: Optional[str]
        text: str
        start: int
        end: int

    @property
    def text(self):
        return self.__text

    @property
    def expression(self):
        return self.__expression

    def __init__(self, text: str):
        self.__algebra = BooleanAlgebra()
        self.__symbols: Dict[int, boolean.Symbol] = {}
        self.__text = text
        self.__values: List["BooleanQuery.Value"] = []

        self.__parse()

    def evaluate(
        self,
        text: str,
        flags: "re._FlagsType" = re.I,
    ):
        """
        Evaluate the query expression against the given text.

        :param text: The text to search.
        :param flags: The regular expression flags to use.
        :return: A boolean indicating whether the expression matches the text.
        """

        values = {
            self.__symbols[key]: (
                self.__algebra.TRUE
                if re.search(
                    re.escape(value.text),
                    text,
                    flags,
                )
                is not None
                else self.__algebra.FALSE
            )
            for key, value in enumerate(self.__values)
        }

        result = self.__expression.subs(values).simplify()

        return result == self.__algebra.TRUE

    def __pair(self, text: str):
        match = re.search(
            r'^[\s\(\)]*-?([^\s:\(\)]+):(\"[^:\(\)"]+\"|[^\s\(\):]+)',
            text,
            re.I,
        )

        if not match:
            return

        start, _ = match.span(1)
        _, end = match.span(2)
        key = match[1]
        text = match[2]

        if key.startswith('"') and key.endswith('"'):
            key = key[1:-1]

        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return BooleanQuery.Value(
            key=key,
            text=text,
            start=start,
            end=end,
        )

    def __word(self, text: str):
        match = re.search(
            r'^[\s\(\)]*-?(\"[^:"-\(\)]+\"|[^:\s\-\(\)]+)',
            text,
            re.I,
        )

        if not match:
            return

        start, end = match.span(1)
        text = match[1]

        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return BooleanQuery.Value(
            key=None,
            text=text,
            start=start,
            end=end,
        )

    def __parse(self):
        n = 0
        index = 0
        text = self.__text

        while True:
            subtext = text[index:]

            if not subtext:
                break

            value = self.__pair(subtext) or self.__word(subtext)

            if not value:
                break

            if value.text.lower() in [
                "and",
                "or",
                "&",
                "|",
            ]:
                index += value.end + 1
                continue

            self.__values.append(value)
            n_str = "n" + str(n)
            self.__symbols[n] = self.__algebra.Symbol(n_str)
            n += 1

            a = value.start + index
            b = value.end + index

            index = a + len(n_str)

            text = text[0:a] + n_str + text[b:]

        text = re.sub(
            r"\s*AND\s*",
            "&",
            text,
            flags=re.I,
        )
        text = re.sub(
            r"\s*OR\s*",
            "|",
            text,
            flags=re.I,
        )
        text = re.sub(
            r"\s*(&|\(|\))\s*",
            lambda match: match[1],
            text,
            flags=re.I,
        )
        text = re.sub(
            r"\s+",
            "&",
            text,
            flags=re.I,
        )
        text = re.sub(
            r"\s+",
            "&",
            text,
            flags=re.I,
        )
        text = re.sub(
            r"-",
            "~",
            text,
            flags=re.I,
        )
        text = re.sub(
            r"(\))([^\)\|&])",
            r"\1&\2",
            text,
            flags=re.I,
        )

        self.__expression = self.__algebra.parse(
            text,
            simplify=True,
        )
