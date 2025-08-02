"""
wKrQ - Weak Kleene logic with restricted quantification.

A three-valued logic system with restricted quantifiers for first-order reasoning.
Based on Ferguson (2021) semantics with tableau-based theorem proving.
"""

from .acrq_parser import SyntaxMode, parse_acrq_formula
from .api import Inference, check_inference
from .formula import (
    BilateralPredicateFormula,
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
from .semantics import BilateralTruthValue, TruthValue, WeakKleeneSemantics
from .signs import F, M, N, Sign, SignedFormula, T
from .tableau import Tableau, TableauResult, entails, solve, valid

__version__ = "1.1.2"

__all__ = [
    # Core types
    "Formula",
    "PropositionalAtom",
    "PredicateFormula",
    "BilateralPredicateFormula",
    "Variable",
    "Constant",
    "Term",
    "RestrictedExistentialFormula",
    "RestrictedUniversalFormula",
    # Semantics
    "WeakKleeneSemantics",
    "TruthValue",
    "BilateralTruthValue",
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
    # ACrQ parser (minimal)
    "parse_acrq_formula",
    "SyntaxMode",
]
