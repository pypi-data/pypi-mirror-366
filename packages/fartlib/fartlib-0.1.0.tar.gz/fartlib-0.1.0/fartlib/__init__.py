from __future__ import annotations
from enum import Enum


class Fart:
    def __init__(self, smell: Smell) -> None:
        self.smell = smell

    def rip(self, power: int = 100) -> None:
        if not power or power <= 0:
            raise ValueError("farts must be powerful.")

        elif power > 100:
            raise ValueError("fart too powerful.")

        print(
            f"letting out a {self.smell} smelling fart with the power score of {power:,} 🤖"
        )


class Smell(Enum):
    HEAVENLY = "heavenly"
    PLEASENT = "pleasent"
    BAD = "bad"
    HORRIBLE = "horrible"
    PUTRID = "putrid"
