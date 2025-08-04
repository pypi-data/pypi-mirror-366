import re
from typing import NamedTuple

RX_PROXY_URI = r"^(https?\:\/\/)(?:([^:@]+):([^@]+)@)?([^:@]+):([^:@]+)$"


class ProxyURI(NamedTuple):
    """
    A named tuple representing a proxy URI with its components parsed.

    This class parses a proxy URI string (like 'http://username:password@host:port')
    into its component parts and provides convenient access to those parts.

    Attributes:
        uri (str): The original proxy URI string.
        protocol (str): The protocol part of the URI (e.g., 'http://').
        username (str): The username for authentication, if present.
        password (str): The password for authentication, if present.
        host (str): The hostname or IP address of the proxy.
        port (str): The port number as a string.
        server (str): The protocol, host, and port combined (without auth).
    """

    uri: str
    protocol: str
    username: str
    password: str
    host: str
    port: str
    server: str

    @staticmethod
    def new(uri: str):
        """
        Create a new ProxyURI instance by parsing a proxy URI string.

        Args:
            uri (str): The proxy URI string to parse, in the format
                      'http(s)://[username:password@]host:port'

        Returns:
            ProxyURI: A new ProxyURI instance with parsed components, or None if
                     the URI couldn't be parsed or is None.

        Examples:
            >>> proxy = ProxyURI.new('http://user:pass@127.0.0.1:8080')
            >>> proxy.username
            'user'
            >>> proxy.host
            '127.0.0.1'
        """
        if uri is None:
            return None

        match = re.search(RX_PROXY_URI, uri)

        if match is None:
            return None

        protocol = match[1]
        username = match[2]
        password = match[3]
        host = match[4]
        port = match[5]
        server = f"{protocol}{host}:{port}"

        return ProxyURI(
            uri=uri,
            protocol=protocol,
            username=username,
            password=password,
            host=host,
            port=port,
            server=server,
        )

    @staticmethod
    def new_dict(
        uri: str,
        remove_empty=True,
    ):
        """
        Create a dictionary representation of a proxy URI's components.

        Args:
            uri (str): The proxy URI string to parse, in the format
                      'http(s)://[username:password@]host:port'
            remove_empty (bool, optional): If True, fields with None values will be
                                          removed from the resulting dictionary.
                                          Defaults to True.

        Returns:
            dict: A dictionary containing the parsed components of the proxy URI,
                 or None if the URI couldn't be parsed or is None.

        Examples:
            >>> proxy_dict = ProxyURI.new_dict('http://user:pass@127.0.0.1:8080')
            >>> proxy_dict['username']
            'user'
            >>> proxy_dict['host']
            '127.0.0.1'
        """
        proxy = ProxyURI.new(uri)

        if proxy is None:
            return None

        result = proxy._asdict()

        if not remove_empty:
            return result

        items = result.items()

        return {k: v for k, v in items if v is not None}
