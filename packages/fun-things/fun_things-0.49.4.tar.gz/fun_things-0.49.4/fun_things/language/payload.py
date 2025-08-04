from dataclasses import dataclass


@dataclass(frozen=True)
class Payload:
    name: str
    code: str
    percent: float
    source: str
