from io import TextIOWrapper
from typing import List, Optional

from .ad_blocker_filter_data import AdBlockerFilterData

try:
    from abp.filters import parse_filterlist
except Exception:
    parse_filterlist = None

try:
    import re2 as re
except Exception:
    import re

DOMAIN_END = (
    "{DOMAIN_END}",
    r"\\\{DOMAIN_END\\\}",
    r"(\/.*)?$",
)


class AdBlockerFilterParser:
    """
    An incredibly watered-down version
    of AdblockPlus' filter parser.

    Uses `pyre2` if it is installed.

    Requires `python-abp`.
    """

    def __init__(self):
        self.clear()

    @property
    def filters(self):
        """
        A generator that yields all filter data objects in the filter list.

        :yields: Filter data objects.
        :rtype: Iterator[FilterData]
        """
        for filder_data in self.__filter_datas:
            yield filder_data

    def clear(self):
        """
        Clears the filter list, emptying it of all filter data.
        """
        self.__filter_datas: List[AdBlockerFilterData] = []

    def add(self, f: TextIOWrapper):
        """
        Reads a filter list from a file object and adds it to the filter list.

        :param f: A file object with a filter list.
        :type f: TextIOWrapper
        """
        if parse_filterlist is None:
            raise ImportError("python-abp is not installed!")

        for line in parse_filterlist(f):
            d = line._asdict()

            if d.get("action") != "block":
                continue

            selector = d["selector"]

            if not selector["value"]:
                continue

            if selector["type"] == "url-pattern":
                if selector["value"].startswith("||"):
                    selector["value"] = selector["value"][2:]

                if selector["value"].endswith("^"):
                    selector["value"] = selector["value"][:-1] + DOMAIN_END[0]

                selector["value"] = re.escape(selector["value"])

                for k, v in [
                    (r"\\\*", ".*"),
                    (r"\\\|", "^"),
                    (DOMAIN_END[1], DOMAIN_END[2]),
                ]:
                    selector["value"] = re.sub(
                        k,
                        v,
                        selector["value"],
                    )

            in_domains = []
            not_in_domains = []

            for k, v in d["options"]:
                if k == "domain":
                    for domain, flag in v:
                        if flag:
                            in_domains.append(domain.lower())
                        else:
                            not_in_domains.append(domain.lower())

            self.__filter_datas.append(
                AdBlockerFilterData(
                    value=re.compile(selector["value"]),
                    in_domains=in_domains,
                    not_in_domains=not_in_domains,
                )
            )

    def should_block(
        self,
        url: str,
        domain: Optional[str] = None,
        case_insensitive: bool = True,
    ):
        """
        Checks if a URL should be blocked according to the filter list.

        :param url: The URL to check.
        :type url: str
        :param domain: The domain of the URL.
        :type domain: Optional[str]
        :param case_insensitive: Whether to perform a case-insensitive match.
        :type case_insensitive: bool
        :return: True if the URL should be blocked, False otherwise.
        :rtype: bool
        """
        for filter_data in self.__filter_datas:
            if filter_data.should_block(
                url,
                domain,
                case_insensitive,
            ):
                return True

        return False
