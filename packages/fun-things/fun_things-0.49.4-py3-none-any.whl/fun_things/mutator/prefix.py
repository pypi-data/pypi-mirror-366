from dataclasses import dataclass
from typing import Any
from .payload import Payload


@dataclass
class Prefix(Payload):
    proceed: bool = True
    """
    If the process should proceed to call the function.
    """
    return_value: Any = None
    """
    This is used if `proceed` is `False`.
    """
