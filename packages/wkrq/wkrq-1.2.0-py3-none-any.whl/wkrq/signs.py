"""
wKrQ sign system for tableau construction.

Signs: T (true), F (false), M (may be true/both), N (need not be true/neither)
These map to truth value sets for semantic evaluation.
"""

from dataclasses import dataclass

from .formula import Formula
from .semantics import FALSE, TRUE, UNDEFINED, TruthValue


@dataclass(frozen=True)
class Sign:
    """A sign in the wKrQ tableau system."""

    symbol: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"Sign({self.symbol})"

    def is_contradictory_with(self, other: "Sign") -> bool:
        """Check if this sign contradicts another sign."""
        # Only T and F contradict each other
        return (self.symbol == "T" and other.symbol == "F") or (
            self.symbol == "F" and other.symbol == "T"
        )

    def truth_conditions(self) -> set[TruthValue]:
        """Get the set of truth values this sign represents."""
        if self.symbol == "T":
            return {TRUE}
        elif self.symbol == "F":
            return {FALSE}
        elif self.symbol == "M":
            return {TRUE, FALSE}  # Both true and false
        elif self.symbol == "N":
            return {UNDEFINED}  # Neither true nor false
        else:
            raise ValueError(f"Unknown sign: {self.symbol}")


# The four signs of wKrQ
T = Sign("T")  # True
F = Sign("F")  # False
M = Sign("M")  # May be true (both)
N = Sign("N")  # Need not be true (neither)

# All valid signs
SIGNS = {T, F, M, N}


@dataclass(frozen=True)
class SignedFormula:
    """A formula with a sign attached."""

    sign: Sign
    formula: Formula

    def __str__(self) -> str:
        return f"{self.sign}: {self.formula}"

    def __repr__(self) -> str:
        return f"SignedFormula({self.sign}, {self.formula})"

    def contradicts(self, other: "SignedFormula") -> bool:
        """Check if this signed formula contradicts another."""
        return self.formula == other.formula and self.sign.is_contradictory_with(
            other.sign
        )


def sign_from_string(s: str) -> Sign:
    """Convert a string to a sign."""
    s = s.upper()
    if s == "T":
        return T
    elif s == "F":
        return F
    elif s == "M":
        return M
    elif s == "N":
        return N
    else:
        raise ValueError(f"Invalid sign: {s}. Must be T, F, M, or N.")
