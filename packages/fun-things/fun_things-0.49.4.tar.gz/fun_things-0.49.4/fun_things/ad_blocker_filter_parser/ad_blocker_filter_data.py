from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class AdBlockerFilterData:
    value: Any
    """
    Regular expression.
    """
    in_domains: List[str]
    """
    Only domains included here will use the filter.
    """
    not_in_domains: List[str]
    """
    Domains included here will NOT use the filter.
    """

    def should_block(
        self,
        url: str,
        domain: Optional[str] = None,
        case_insensitive: bool = True,
    ):
        """
        Check if the given url should be blocked by this filter.

        :param url: The URL to check.
        :param domain: The domain of the URL.
        :param case_insensitive: Whether to do a case insensitive search.
        :return: True if the URL should be blocked, False otherwise.
        """
        if domain is not None:
            if case_insensitive:
                domain = domain.lower()

            if self.not_in_domains and domain in self.not_in_domains:
                return False

            if self.in_domains and domain not in self.in_domains:
                return False

        if case_insensitive:
            url = url.lower()

        return self.value.search(url) is not None
