"""
wKrQ - Weak Kleene logic with restricted quantification.

A three-valued logic system with restricted quantifiers for first-order reasoning.
Based on Ferguson (2021) semantics with tableau-based theorem proving.
"""

from .api import Inference, check_inference
from .formula import (
    Constant,
    Formula,
    PredicateFormula,
    PropositionalAtom,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    Term,
    Variable,
)
from .parser import parse, parse_inference
from .semantics import TruthValue, WeakKleeneSemantics
from .signs import F, M, N, Sign, SignedFormula, T
from .tableau import Tableau, TableauResult, entails, solve, valid

__version__ = "1.0.6"

__all__ = [
    # Core types
    "Formula",
    "PropositionalAtom",
    "PredicateFormula",
    "Variable",
    "Constant",
    "Term",
    "RestrictedExistentialFormula",
    "RestrictedUniversalFormula",
    # Semantics
    "WeakKleeneSemantics",
    "TruthValue",
    # Signs
    "Sign",
    "SignedFormula",
    "T",
    "F",
    "M",
    "N",
    # Tableau
    "Tableau",
    "TableauResult",
    # Main functions
    "solve",
    "valid",
    "entails",
    "parse",
    "parse_inference",
    "check_inference",
    "Inference",
]
