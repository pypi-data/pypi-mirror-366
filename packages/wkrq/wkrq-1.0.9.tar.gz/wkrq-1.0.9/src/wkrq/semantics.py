"""
wKrQ three-valued weak Kleene semantics.

Implements the truth value system and semantic operations for wKrQ logic.
Truth values: t (true), e (undefined), f (false)
"""

from collections.abc import Generator
from dataclasses import dataclass


@dataclass(frozen=True)
class TruthValue:
    """A truth value in weak Kleene logic."""

    symbol: str
    name: str

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"TruthValue({self.symbol}, {self.name})"


# The three truth values of weak Kleene logic
TRUE = TruthValue("t", "true")
UNDEFINED = TruthValue("e", "undefined")
FALSE = TruthValue("f", "false")


class WeakKleeneSemantics:
    """Three-valued weak Kleene semantic system."""

    def __init__(self) -> None:
        self.truth_values = {TRUE, UNDEFINED, FALSE}
        self.designated_values = {TRUE}

        # Truth tables for connectives
        self._conjunction_table = self._build_conjunction_table()
        self._disjunction_table = self._build_disjunction_table()
        self._negation_table = self._build_negation_table()
        self._implication_table = self._build_implication_table()

    def _build_conjunction_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene conjunction truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): FALSE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): FALSE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): FALSE,
        }

    def _build_disjunction_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene disjunction truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): TRUE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): TRUE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): FALSE,
        }

    def _build_negation_table(self) -> dict[TruthValue, TruthValue]:
        """Build weak Kleene negation truth table."""
        return {TRUE: FALSE, UNDEFINED: UNDEFINED, FALSE: TRUE}

    def _build_implication_table(self) -> dict[tuple, TruthValue]:
        """Build weak Kleene implication truth table."""
        return {
            (TRUE, TRUE): TRUE,
            (
                TRUE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (TRUE, FALSE): FALSE,
            (
                UNDEFINED,
                TRUE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (UNDEFINED, UNDEFINED): UNDEFINED,
            (
                UNDEFINED,
                FALSE,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, TRUE): TRUE,
            (
                FALSE,
                UNDEFINED,
            ): UNDEFINED,  # Weak Kleene: any undefined input → undefined output
            (FALSE, FALSE): TRUE,
        }

    def conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute conjunction of two truth values."""
        return self._conjunction_table[(a, b)]

    def disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute disjunction of two truth values."""
        return self._disjunction_table[(a, b)]

    def negation(self, a: TruthValue) -> TruthValue:
        """Compute negation of a truth value."""
        return self._negation_table[a]

    def implication(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """Compute implication of two truth values."""
        return self._implication_table[(a, b)]

    def evaluate_connective(self, connective: str, *args: TruthValue) -> TruthValue:
        """Evaluate a connective with given truth value arguments."""
        if connective in ["&", "'", "∧"]:
            return self.conjunction(args[0], args[1])
        elif connective in ["|", "(", "∨"]:
            return self.disjunction(args[0], args[1])
        elif connective in ["~", "¬"]:
            return self.negation(args[0])
        elif connective in ["->", "→"]:
            return self.implication(args[0], args[1])
        else:
            raise ValueError(f"Unknown connective: {connective}")

    def is_designated(self, value: TruthValue) -> bool:
        """Check if a truth value is designated (true)."""
        return value in self.designated_values

    def all_valuations(
        self, atoms: set[str]
    ) -> Generator[dict[str, TruthValue], None, None]:
        """Generate all possible truth valuations for a set of atoms."""
        import itertools

        atoms_list = sorted(list(atoms))
        for values in itertools.product(self.truth_values, repeat=len(atoms_list)):
            yield dict(zip(atoms_list, values))
