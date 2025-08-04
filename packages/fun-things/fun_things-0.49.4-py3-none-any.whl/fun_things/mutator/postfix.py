from dataclasses import dataclass
from typing import Any
from .payload import Payload


@dataclass
class Postfix(Payload):
    return_value: Any
