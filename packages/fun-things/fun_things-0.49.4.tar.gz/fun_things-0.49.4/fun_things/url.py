from typing import Union
from urllib.parse import ParseResult, quote, unquote, urlparse, urlunparse


def re_escape_special_chars(
    text: str,
    safe: str = "/",
):
    """
    Decode and re-encode URL components to normalize escaped characters.

    This function decodes URL-encoded special characters (like %20) and then
    re-encodes them in a consistent way. It's useful for normalizing URLs
    that may have been encoded multiple times or inconsistently.

    Args:
        text (str): The URL component text to process.
        safe (str, optional): Characters that should not be percent-encoded.
                              Defaults to "/".

    Returns:
        str: The normalized URL component with consistent escaping.
    """
    for _ in range(10):
        new_text = unquote(text)

        if new_text == text:
            break

        text = new_text

    return quote(
        text,
        safe=safe,
    )


def re_escape_url(value: Union[str, ParseResult]):
    """
    Normalize and re-escape an entire URL.

    This function takes a URL (either as a string or ParseResult) and normalizes
    the escaping of special characters in each component of the URL. It's useful
    for ensuring consistent URL encoding, especially when dealing with URLs that
    may have been encoded multiple times or inconsistently.

    Args:
        value (Union[str, ParseResult]): The URL to normalize, either as a string
                                         or as a ParseResult object.

    Returns:
        str: The normalized URL with consistent escaping across all components.

    Note:
        Different URL components have different 'safe' characters that don't need
        escaping, which this function handles appropriately.
    """
    try:
        url = value

        if isinstance(url, str):
            url = urlparse(url)

        url = url._replace(
            path=re_escape_special_chars(url.path, safe="/@"),
            params=re_escape_special_chars(url.params),
            query=re_escape_special_chars(url.query, safe="=&"),
            fragment=re_escape_special_chars(url.fragment),
        )

        return urlunparse(url)

    except Exception:
        pass

    if isinstance(value, str):
        return value

    return urlunparse(value)
