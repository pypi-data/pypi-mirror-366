from dataclasses import dataclass


@dataclass
class Payload:
    args: list
    kwargs: dict
