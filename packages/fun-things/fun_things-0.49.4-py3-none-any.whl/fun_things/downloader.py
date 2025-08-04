from dataclasses import dataclass
from time import perf_counter
from typing import List, Optional
import requests


@dataclass
class Chunk:
    value: List[bytes]
    b: int
    speed_b: float
    destination: Optional[str]
    cancel: bool = False
    """
    Set to `false` to stop downloading.
    """

    @property
    def kb(self):
        return self.b / 1024

    @property
    def mb(self):
        return self.kb / 1024

    @property
    def speed_kb(self):
        return self.speed_b / 1024

    @property
    def speed_mb(self):
        return self.speed_kb / 1024


def download(
    url: str,
    destination: Optional[str] = None,
):
    with requests.get(
        url,
        stream=True,
    ) as r:
        t1 = perf_counter()
        b = 0

        r.raise_for_status()

        f = open(destination, "wb") if destination else None

        for chunk in r.iter_content(chunk_size=8192):
            t2 = perf_counter()
            b += len(chunk)
            speed_b = b // (t2 - t1)

            if f is not None:
                f.write(chunk)

            response = Chunk(
                b=b,
                speed_b=speed_b,
                value=chunk,
                destination=destination,
            )

            yield response

            if response.cancel:
                break

        if f is not None:
            f.close()
