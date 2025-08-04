from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Affix:
    priority: int
    fn: Callable
