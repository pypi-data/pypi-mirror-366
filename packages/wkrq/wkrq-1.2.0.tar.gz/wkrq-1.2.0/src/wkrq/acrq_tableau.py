"""
ACrQ-specific tableau implementation with bilateral predicate support.

This module extends the standard wKrQ tableau to handle bilateral predicates
according to Ferguson's ACrQ system.
"""

from dataclasses import dataclass, field
from typing import Optional

from .formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Formula,
    PredicateFormula,
)
from .semantics import FALSE, BilateralTruthValue, TruthValue
from .signs import F, M, N, SignedFormula, T
from .tableau import Branch, Model, RuleInfo, RuleType, Tableau


class ACrQBranch(Branch):
    """Branch for ACrQ tableau with paraconsistent contradiction detection."""

    def __init__(self, branch_id: int):
        """Initialize ACrQ branch."""
        super().__init__(branch_id)
        self.bilateral_pairs: dict[str, str] = {}  # Maps R to R*

    def _check_contradiction(self, new_formula: SignedFormula) -> bool:
        """Check for contradictions with ACrQ paraconsistent rules."""
        # Standard contradiction check for non-bilateral predicates
        if super()._check_contradiction(new_formula):
            return True

        # For ACrQ, we allow T:R(a) and T:R*(a) to coexist (paraconsistent)
        # This represents a "glut" - conflicting information
        # We only check for contradictions in the standard wKrQ sense

        # Note: In a full ACrQ implementation, we might want to track gluts
        # and gaps explicitly, but for paraconsistency, we simply don't
        # close branches on bilateral contradictions

        return False


@dataclass
class ACrQModel(Model):
    """Model for ACrQ with bilateral predicate support."""

    bilateral_valuations: dict[str, BilateralTruthValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize bilateral valuations from standard valuations."""
        super().__init__(self.valuations, self.constants)
        self.bilateral_valuations = {}

        # Group predicates by base name
        bilateral_predicates: dict[str, dict[str, dict[str, TruthValue]]] = {}

        for atom_str, value in self.valuations.items():
            # Skip propositional atoms
            if "(" not in atom_str:
                continue

            # Extract predicate name and arguments
            pred_name = atom_str.split("(")[0]
            args = "(" + atom_str.split("(", 1)[1]

            # Determine base name
            if pred_name.endswith("*"):
                base_name = pred_name[:-1]
                is_negative = True
            else:
                base_name = pred_name
                is_negative = False

            # Initialize structure if needed
            if base_name not in bilateral_predicates:
                bilateral_predicates[base_name] = {}

            key = f"{base_name}{args}"
            if key not in bilateral_predicates[base_name]:
                bilateral_predicates[base_name][key] = {
                    "positive": FALSE,
                    "negative": FALSE,
                }

            # Set the appropriate value
            if is_negative:
                bilateral_predicates[base_name][key]["negative"] = value
            else:
                bilateral_predicates[base_name][key]["positive"] = value

        # Create bilateral truth values
        for _base_name, pred_instances in bilateral_predicates.items():
            for key, values in pred_instances.items():
                btv = BilateralTruthValue(
                    positive=values["positive"], negative=values["negative"]
                )
                self.bilateral_valuations[key] = btv


class ACrQTableau(Tableau):
    """Extended tableau for ACrQ with bilateral predicate support."""

    def __init__(self, initial_formulas: list[SignedFormula]) -> None:
        """Initialize ACrQ tableau with bilateral predicate tracking."""
        self.bilateral_pairs: dict[str, str] = (
            {}
        )  # Maps R to R* - Initialize before super()
        super().__init__(initial_formulas)
        self.logic_system = "ACrQ"

        # Identify bilateral predicates in initial formulas
        self._identify_bilateral_predicates(initial_formulas)

    def _identify_bilateral_predicates(self, formulas: list[SignedFormula]) -> None:
        """Identify and register bilateral predicate pairs."""
        for sf in formulas:
            self._extract_bilateral_pairs(sf.formula)

    def _extract_bilateral_pairs(self, formula: Formula) -> None:
        """Extract bilateral predicate pairs from a formula."""
        if isinstance(formula, BilateralPredicateFormula):
            # Register both R -> R* and R* -> R mappings
            pos_name = formula.positive_name
            neg_name = f"{formula.positive_name}*"
            self.bilateral_pairs[pos_name] = neg_name
            self.bilateral_pairs[neg_name] = pos_name

        elif isinstance(formula, CompoundFormula):
            for sub in formula.subformulas:
                self._extract_bilateral_pairs(sub)

        elif hasattr(formula, "restriction") and hasattr(formula, "matrix"):
            # Handle quantified formulas
            self._extract_bilateral_pairs(formula.restriction)
            self._extract_bilateral_pairs(formula.matrix)

    def _create_branch(self, branch_id: int) -> ACrQBranch:
        """Create an ACrQ branch with paraconsistent contradiction detection."""
        branch = ACrQBranch(branch_id)
        branch.bilateral_pairs = self.bilateral_pairs.copy()
        return branch

    def _get_applicable_rule(
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get applicable rule, including ACrQ-specific rules."""
        # Try ACrQ-specific rules first
        acrq_rule = self._get_acrq_rule(signed_formula, branch)
        if acrq_rule:
            return acrq_rule

        # Fall back to standard rules
        return super()._get_applicable_rule(signed_formula, branch)

    def _get_acrq_rule(
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get ACrQ-specific tableau rules for bilateral predicates."""
        formula = signed_formula.formula

        # Handle bilateral predicates
        if isinstance(formula, BilateralPredicateFormula):
            return self._get_bilateral_predicate_rule(signed_formula, branch)

        # Handle negation of bilateral predicates
        elif isinstance(formula, CompoundFormula) and formula.connective == "~":
            return self._get_bilateral_negation_rule(signed_formula)

        return None

    def _get_bilateral_predicate_rule(
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get tableau rules for bilateral predicates."""
        formula = signed_formula.formula
        if not isinstance(formula, BilateralPredicateFormula):
            return None

        sign = signed_formula.sign

        # Check if already processed to avoid infinite loops
        if (
            hasattr(branch, "_processed_formulas")
            and signed_formula in branch._processed_formulas
        ):
            return None

        pos_pred, neg_pred = formula.to_standard_predicates()

        if sign == T:
            return self._get_t_bilateral_rule(formula, pos_pred, neg_pred)
        elif sign == F:
            return self._get_f_bilateral_rule(formula, pos_pred, neg_pred)
        elif sign == M:
            return self._get_m_bilateral_rule(formula, pos_pred, neg_pred)
        elif sign == N:
            return self._get_n_bilateral_rule(formula, pos_pred, neg_pred)

        return None

    def _get_t_bilateral_rule(
        self,
        formula: BilateralPredicateFormula,
        pos_pred: PredicateFormula,
        neg_pred: PredicateFormula,
    ) -> RuleInfo:
        """Get T-sign rule for bilateral predicates."""
        if formula.is_negative:
            # T: R*(x) just means R*(x) is true - says nothing about R(x)
            # This is key to paraconsistency - R(x) and R*(x) are independent
            conclusions = [[SignedFormula(T, neg_pred)]]
            return RuleInfo("T-R*", RuleType.ALPHA, 1, 1, conclusions)
        else:
            # T: R(x) just means R(x) is true - says nothing about R*(x)
            conclusions = [[SignedFormula(T, pos_pred)]]
            return RuleInfo("T-R", RuleType.ALPHA, 1, 1, conclusions)

    def _get_f_bilateral_rule(
        self,
        formula: BilateralPredicateFormula,
        pos_pred: PredicateFormula,
        neg_pred: PredicateFormula,
    ) -> RuleInfo:
        """Get F-sign rule for bilateral predicates."""
        if formula.is_negative:
            # F: R*(x) just means R*(x) is false - says nothing about R(x)
            conclusions = [[SignedFormula(F, neg_pred)]]
            return RuleInfo("F-R*", RuleType.ALPHA, 1, 1, conclusions)
        else:
            # F: R(x) just means R(x) is false - says nothing about R*(x)
            conclusions = [[SignedFormula(F, pos_pred)]]
            return RuleInfo("F-R", RuleType.ALPHA, 1, 1, conclusions)

    def _get_m_bilateral_rule(
        self,
        formula: BilateralPredicateFormula,
        pos_pred: PredicateFormula,
        neg_pred: PredicateFormula,
    ) -> RuleInfo:
        """Get M-sign rule for bilateral predicates."""
        if formula.is_negative:
            # M: R*(x) - focus on R*
            conclusions = [
                [SignedFormula(T, neg_pred)],  # R* is true
                [SignedFormula(F, neg_pred)],  # R* is false
            ]
        else:
            # M: R(x) - focus on R
            conclusions = [
                [SignedFormula(T, pos_pred)],  # R is true
                [SignedFormula(F, pos_pred)],  # R is false
            ]
        return RuleInfo(
            f"M-R{'*' if formula.is_negative else ''}",
            RuleType.BETA,
            20,
            2,
            conclusions,
        )

    def _get_n_bilateral_rule(
        self,
        formula: BilateralPredicateFormula,
        pos_pred: PredicateFormula,
        neg_pred: PredicateFormula,
    ) -> RuleInfo:
        """Get N-sign rule for bilateral predicates."""
        # N: R(x) means R(x) is undefined
        # In bilateral interpretation, this means gap (both false)
        conclusions = [[SignedFormula(F, pos_pred), SignedFormula(F, neg_pred)]]
        return RuleInfo(
            f"N-R{'*' if formula.is_negative else ''}",
            RuleType.ALPHA,
            5,
            2,
            conclusions,
        )

    def _get_bilateral_negation_rule(
        self, signed_formula: SignedFormula
    ) -> Optional[RuleInfo]:
        """Get rule for negation of bilateral predicates."""
        formula = signed_formula.formula
        if not isinstance(formula, CompoundFormula):
            return None

        sign = signed_formula.sign

        sub = formula.subformulas[0]
        if isinstance(sub, BilateralPredicateFormula):
            # ¬R(x) becomes R*(x) and ¬R*(x) becomes R(x)
            dual = BilateralPredicateFormula(
                positive_name=sub.positive_name,
                terms=sub.terms,
                is_negative=not sub.is_negative,
            )
            conclusions = [[SignedFormula(sign, dual)]]
            return RuleInfo("Bilateral-Negation", RuleType.ALPHA, 0, 1, conclusions)

        return None

    def _extract_model(self, branch: Branch) -> Optional[ACrQModel]:
        """Extract an ACrQ model from an open branch."""
        # Use base class to get standard model
        base_model = super()._extract_model(branch)

        if base_model is None:
            return None

        # Create ACrQ model with bilateral valuations
        acrq_model = ACrQModel(
            valuations=base_model.valuations, constants=base_model.constants
        )

        return acrq_model
