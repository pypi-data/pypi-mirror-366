import socket
from time import perf_counter


def ping(
    host="8.8.8.8",
    port=53,
    timeout=3,
):
    """
    Measures the time it takes to establish a TCP connection to a given host and port.

    Args:
        host (str): The host to connect to. Defaults to "8.8.8.8".
        port (int): The port to connect to. Defaults to 53.
        timeout (int): The timeout for the connection attempt in seconds. Defaults to 3.

    Returns:
        float: The time elapsed in seconds to establish the connection.

    Raises:
        socket.error: If an error occurs while attempting to connect.
    """

    try:
        t1 = perf_counter()

        socket.setdefaulttimeout(timeout)

        conn = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        conn.connect((host, port))

        elapsed_time = perf_counter() - t1

        conn.close()

        return elapsed_time

    except socket.error as e:
        print(e)
        pass
