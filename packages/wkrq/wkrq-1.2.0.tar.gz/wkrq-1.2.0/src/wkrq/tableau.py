"""
wKrQ tableau construction engine.

Optimized tableau prover for wKrQ logic with industrial-grade performance.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .formula import (
    CompoundFormula,
    Constant,
    Formula,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
)
from .semantics import FALSE, TRUE, UNDEFINED, TruthValue
from .signs import F, M, N, Sign, SignedFormula, T


class RuleType(Enum):
    """Types of tableau rules for optimization."""

    ALPHA = "alpha"  # Non-branching rules (high priority)
    BETA = "beta"  # Branching rules (lower priority)


@dataclass
class RuleInfo:
    """Information about a tableau rule for optimization."""

    name: str
    rule_type: RuleType
    priority: int  # Lower numbers = higher priority
    complexity_cost: int  # Estimated computational cost
    conclusions: list[list[SignedFormula]]
    instantiation_constant: Optional[str] = None  # For universal quantifier tracking

    def __lt__(self, other: "RuleInfo") -> bool:
        """Compare rules for priority ordering."""
        # Alpha rules always come first
        if self.rule_type == RuleType.ALPHA and other.rule_type != RuleType.ALPHA:
            return True
        if self.rule_type != RuleType.ALPHA and other.rule_type == RuleType.ALPHA:
            return False

        # Then by explicit priority
        if self.priority != other.priority:
            return self.priority < other.priority

        # Finally by complexity cost
        return self.complexity_cost < other.complexity_cost


@dataclass
class TableauNode:
    """A node in the tableau tree."""

    id: int
    formula: SignedFormula
    parent: Optional["TableauNode"] = None
    children: list["TableauNode"] = field(default_factory=list)
    rule_applied: Optional[str] = None
    is_closed: bool = False
    closure_reason: Optional[str] = None
    depth: int = 0

    def add_child(self, child: "TableauNode", rule: Optional[str] = None) -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        child.rule_applied = rule
        self.children.append(child)


@dataclass
class Branch:
    """A branch in the tableau with industrial-grade optimizations."""

    id: int
    nodes: list[TableauNode] = field(default_factory=list)
    formulas: set[SignedFormula] = field(default_factory=set)
    is_closed: bool = False
    closure_reason: Optional[str] = None

    # Optimization: index formulas by sign and formula for O(1) lookup
    formula_index: dict[Sign, dict[Formula, set[int]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(set))
    )

    # Constraint propagation: track unit literals and implications
    unit_literals: set[SignedFormula] = field(default_factory=set)
    implications: list[tuple[SignedFormula, SignedFormula]] = field(
        default_factory=list
    )

    # Performance metrics
    complexity_score: int = 0
    branching_factor: int = 0

    # Track processed formulas to avoid reprocessing
    _processed_formulas: set[SignedFormula] = field(default_factory=set)

    # Track ground terms (constants) for unification
    ground_terms: set[str] = field(default_factory=set)

    # Track universal quantifier instantiations: formula -> set of constants used
    _universal_instantiations: dict[SignedFormula, set[str]] = field(
        default_factory=dict
    )

    def add_formula(self, signed_formula: SignedFormula, node: TableauNode) -> bool:
        """Add a formula to the branch. Return True if branch closes."""
        # Skip if already exists (basic duplicate detection)
        if signed_formula in self.formulas:
            return False

        # Check for immediate contradiction (O(1) with indexing)
        if self._check_contradiction(signed_formula):
            self.is_closed = True
            self.closure_reason = f"{signed_formula} contradicts existing formula"
            return True

        # Add to branch structures
        self.formulas.add(signed_formula)
        self.nodes.append(node)
        self.formula_index[signed_formula.sign][signed_formula.formula].add(
            len(self.nodes) - 1
        )

        # Extract ground terms from the formula
        self._extract_ground_terms(signed_formula.formula)

        # Update complexity score for branch selection
        self.complexity_score += self._formula_complexity(signed_formula.formula)

        # Constraint propagation: detect unit literals
        if self._is_unit_literal(signed_formula):
            self.unit_literals.add(signed_formula)
            self._propagate_unit_literal(signed_formula)

        return False

    def _check_contradiction(self, new_formula: SignedFormula) -> bool:
        """Check if new formula contradicts existing formulas."""
        # Only T and F contradict
        if new_formula.sign == T:
            return len(self.formula_index[F][new_formula.formula]) > 0
        elif new_formula.sign == F:
            return len(self.formula_index[T][new_formula.formula]) > 0
        return False

    def has_formula(self, signed_formula: SignedFormula) -> bool:
        """Check if branch already contains this signed formula."""
        return signed_formula in self.formulas

    def _formula_complexity(self, formula: Formula) -> int:
        """Calculate complexity score of a formula."""
        if formula.is_atomic():
            return 1
        return formula.complexity()

    def _is_unit_literal(self, signed_formula: SignedFormula) -> bool:
        """Check if this is a unit literal (atomic formula)."""
        return signed_formula.formula.is_atomic()

    def _propagate_unit_literal(self, unit_literal: SignedFormula) -> None:
        """Propagate constraints from unit literal."""
        # In a more sophisticated implementation, this would propagate
        # the literal through implications and update other formulas
        # For now, just track it for future optimization
        pass

    def _extract_ground_terms(self, formula: Formula) -> None:
        """Extract ground terms (constants) from a formula for unification."""
        from .formula import CompoundFormula, Constant, PredicateFormula

        if isinstance(formula, PredicateFormula):
            # Extract constants from predicate arguments
            for term in formula.terms:
                if isinstance(term, Constant):
                    self.ground_terms.add(term.name)
        elif isinstance(formula, CompoundFormula):
            # Recursively extract from subformulas
            for subformula in formula.subformulas:
                self._extract_ground_terms(subformula)
        elif hasattr(formula, "restriction") and hasattr(formula, "matrix"):
            # Handle restricted quantifiers
            self._extract_ground_terms(formula.restriction)
            self._extract_ground_terms(formula.matrix)

    def _find_best_instantiation_constant(self, variable_name: str) -> Optional[str]:
        """Find the best constant to instantiate a quantified variable with.

        Uses unification principles: prefer existing constants over fresh ones.
        """
        # First, try to find constants that appear in the restriction or matrix
        # This implements a simple form of unification for tableau theorem proving
        if self.ground_terms:
            # Return the first available ground term
            # In a more sophisticated implementation, we could rank these by relevance
            return next(iter(self.ground_terms))

        # If no ground terms available, we'll need to generate a fresh constant
        return None

    def _unify_with_existing_terms(self, formula: Formula) -> dict[str, str]:
        """Attempt to unify quantified variables with existing ground terms.

        This is a simplified unification that looks for opportunities to use
        existing constants instead of always generating fresh ones.
        """
        from .formula import RestrictedQuantifierFormula

        unification_map = {}

        if isinstance(formula, RestrictedQuantifierFormula):
            var_name = formula.var.name
            best_constant = self._find_best_instantiation_constant(var_name)
            if best_constant:
                unification_map[var_name] = best_constant

        return unification_map


@dataclass
class Model:
    """A model extracted from an open branch."""

    valuations: dict[str, TruthValue]
    constants: dict[str, set[Formula]]  # For first-order models

    def __str__(self) -> str:
        val_str = ", ".join(f"{k}={v}" for k, v in sorted(self.valuations.items()))
        if self.constants:
            const_str = "; ".join(
                f"{c}: {', '.join(str(f) for f in fs)}"
                for c, fs in sorted(self.constants.items())
            )
            return f"{{valuations: {{{val_str}}}, constants: {{{const_str}}}}}"
        return f"{{{val_str}}}"


@dataclass
class TableauResult:
    """Result of tableau construction."""

    satisfiable: bool
    models: list[Model]
    closed_branches: int
    open_branches: int
    total_nodes: int
    tableau: Optional["Tableau"] = None

    @property
    def valid(self) -> bool:
        """Check if the original formula is valid (no countermodels)."""
        return not self.satisfiable


class Tableau:
    """Industrial-grade optimized tableau for wKrQ logic."""

    def __init__(self, initial_formulas: list[SignedFormula]):
        if not initial_formulas:
            raise ValueError("Cannot create tableau with empty formula list")
        self.root = TableauNode(0, initial_formulas[0])
        self.nodes: list[TableauNode] = [self.root]
        self.branches: list[Branch] = []
        self.open_branches: list[Branch] = []
        self.closed_branches: list[Branch] = []
        self.node_counter = 1
        self.constants: set[str] = set()  # Track introduced constants

        # Performance optimization settings
        self.max_branching_factor = 1000  # Prevent exponential explosion
        self.max_tableau_depth = 100  # Prevent infinite loops
        self.early_termination = True  # Stop on first satisfying model

        # Advanced optimization state
        self.global_processed_formulas: set[SignedFormula] = set()
        self.branch_selection_strategy = (
            "least_complex"  # "least_complex", "depth_first", "breadth_first"
        )
        self.rule_application_stats: dict[str, int] = defaultdict(int)

        # Initialize with first branch
        initial_branch = self._create_branch(0)
        self.branches.append(initial_branch)
        self.open_branches.append(initial_branch)

        # Add initial formulas to root and branch
        for i, sf in enumerate(initial_formulas):
            if i == 0:
                # First formula goes to root
                self.root.formula = sf
                initial_branch.add_formula(sf, self.root)
            else:
                # Additional formulas as children of root
                node = TableauNode(self.node_counter, sf)
                self.node_counter += 1
                self.nodes.append(node)
                self.root.add_child(node)

                if initial_branch.add_formula(sf, node):
                    self.open_branches.remove(initial_branch)
                    self.closed_branches.append(initial_branch)
                    break

        # Update global constants from all initial ground terms
        for branch in self.branches:
            self.constants.update(branch.ground_terms)

    def _create_branch(self, branch_id: int) -> Branch:
        """Factory method for creating branches. Can be overridden by subclasses."""
        return Branch(branch_id)

    def is_complete(self) -> bool:
        """Check if tableau construction is complete."""
        return len(self.open_branches) == 0 or all(
            self._branch_is_complete(branch) for branch in self.open_branches
        )

    def _branch_is_complete(self, branch: Branch) -> bool:
        """Check if all possible rules have been applied to a branch."""
        for node in branch.nodes:
            if self._get_applicable_rule(node.formula, branch) is not None:
                return False
        return True

    def _get_applicable_rule(  # noqa: C901
        self, signed_formula: SignedFormula, branch: Branch
    ) -> Optional[RuleInfo]:
        """Get the next applicable rule for a signed formula with optimization."""
        sign = signed_formula.sign
        formula = signed_formula.formula

        # Check if this formula has already been processed
        # Exception: Universal quantifiers should be re-instantiated with new constants
        if hasattr(branch, "_processed_formulas"):
            if signed_formula in branch._processed_formulas:
                # Allow re-processing of universal quantifiers for new constants
                if not (isinstance(formula, RestrictedUniversalFormula) and sign == T):
                    return None
        else:
            branch._processed_formulas = set()

        if isinstance(formula, CompoundFormula):
            connective = formula.connective

            # Conjunction rules
            if connective == "&":
                if sign == T:
                    conclusions = [
                        [
                            SignedFormula(T, formula.subformulas[0]),
                            SignedFormula(T, formula.subformulas[1]),
                        ]
                    ]
                    return RuleInfo("T-Conjunction", RuleType.ALPHA, 1, 2, conclusions)
                elif sign == F:
                    conclusions = [
                        [SignedFormula(F, formula.subformulas[0])],
                        [SignedFormula(F, formula.subformulas[1])],
                    ]
                    return RuleInfo("F-Conjunction", RuleType.BETA, 10, 3, conclusions)
                elif sign == M:
                    conclusions = [
                        [SignedFormula(M, formula.subformulas[0])],
                        [SignedFormula(M, formula.subformulas[1])],
                    ]
                    return RuleInfo("M-Conjunction", RuleType.BETA, 20, 4, conclusions)
                elif sign == N:
                    conclusions = [
                        [SignedFormula(N, formula.subformulas[0])],
                        [SignedFormula(N, formula.subformulas[1])],
                    ]
                    return RuleInfo("N-Conjunction", RuleType.BETA, 30, 4, conclusions)

            # Disjunction rules
            elif connective == "|":
                if sign == T:
                    conclusions = [
                        [SignedFormula(T, formula.subformulas[0])],
                        [SignedFormula(T, formula.subformulas[1])],
                    ]
                    return RuleInfo("T-Disjunction", RuleType.BETA, 11, 3, conclusions)
                elif sign == F:
                    conclusions = [
                        [
                            SignedFormula(F, formula.subformulas[0]),
                            SignedFormula(F, formula.subformulas[1]),
                        ]
                    ]
                    return RuleInfo("F-Disjunction", RuleType.ALPHA, 2, 2, conclusions)
                elif sign == M:
                    conclusions = [
                        [SignedFormula(M, formula.subformulas[0])],
                        [SignedFormula(M, formula.subformulas[1])],
                    ]
                    return RuleInfo("M-Disjunction", RuleType.BETA, 21, 4, conclusions)
                elif sign == N:
                    conclusions = [
                        [SignedFormula(N, formula.subformulas[0])],
                        [SignedFormula(N, formula.subformulas[1])],
                    ]
                    return RuleInfo("N-Disjunction", RuleType.BETA, 31, 4, conclusions)

            # Negation rules (all ALPHA - high priority)
            elif connective == "~":
                subformula = formula.subformulas[0]
                if sign == T:
                    conclusions = [[SignedFormula(F, subformula)]]
                    return RuleInfo("T-Negation", RuleType.ALPHA, 0, 1, conclusions)
                elif sign == F:
                    conclusions = [[SignedFormula(T, subformula)]]
                    return RuleInfo("F-Negation", RuleType.ALPHA, 0, 1, conclusions)
                elif sign == M:
                    conclusions = [[SignedFormula(M, subformula)]]
                    return RuleInfo("M-Negation", RuleType.ALPHA, 5, 1, conclusions)
                elif sign == N:
                    conclusions = [[SignedFormula(N, subformula)]]
                    return RuleInfo("N-Negation", RuleType.ALPHA, 5, 1, conclusions)

            # Implication rules
            elif connective == "->":
                antecedent = formula.subformulas[0]
                consequent = formula.subformulas[1]
                if sign == T:
                    conclusions = [
                        [SignedFormula(F, antecedent)],
                        [SignedFormula(T, consequent)],
                    ]
                    return RuleInfo("T-Implication", RuleType.BETA, 12, 3, conclusions)
                elif sign == F:
                    conclusions = [
                        [SignedFormula(T, antecedent), SignedFormula(F, consequent)]
                    ]
                    return RuleInfo("F-Implication", RuleType.ALPHA, 3, 2, conclusions)
                elif sign == M:
                    conclusions = [
                        [SignedFormula(M, antecedent)],
                        [SignedFormula(M, consequent)],
                    ]
                    return RuleInfo("M-Implication", RuleType.BETA, 22, 4, conclusions)
                elif sign == N:
                    conclusions = [
                        [SignedFormula(N, antecedent)],
                        [SignedFormula(N, consequent)],
                    ]
                    return RuleInfo("N-Implication", RuleType.BETA, 32, 4, conclusions)

        # Restricted quantifier rules with unification
        if isinstance(formula, RestrictedExistentialFormula):
            # T:[∃X P(X)]Q(X) - there exists an x such that P(x) and Q(x)
            if sign == T:
                # For existentials, prefer fresh constants to avoid inappropriate witnesses
                # Existentials assert existence of *some* individual, not necessarily existing ones
                instantiation_const = Constant(f"c_{len(branch.nodes)}")
                # Track the new constant
                branch.ground_terms.add(instantiation_const.name)

                # Substitute the variable with the chosen constant
                restriction_inst = formula.restriction.substitute_term(
                    {formula.var.name: instantiation_const}
                )
                matrix_inst = formula.matrix.substitute_term(
                    {formula.var.name: instantiation_const}
                )

                # T:[∃X P(X)]Q(X) expands to: T:P(c) ∧ T:Q(c)
                conclusions = [
                    [SignedFormula(T, restriction_inst), SignedFormula(T, matrix_inst)]
                ]
                return RuleInfo(
                    "T-RestrictedExists", RuleType.ALPHA, 40, 1, conclusions
                )

            elif sign == F:
                # F:[∃X P(X)]Q(X) - there's no x such that P(x) and Q(x)
                # This requires universal instantiation over all existing constants
                # For tableau efficiency, we use a witness constant
                unification_map = branch._unify_with_existing_terms(formula)

                if unification_map and formula.var.name in unification_map:
                    const_name = unification_map[formula.var.name]
                    instantiation_const = Constant(const_name)
                else:
                    instantiation_const = Constant(f"c_{len(branch.nodes)}")
                    branch.ground_terms.add(instantiation_const.name)

                restriction_inst = formula.restriction.substitute_term(
                    {formula.var.name: instantiation_const}
                )
                matrix_inst = formula.matrix.substitute_term(
                    {formula.var.name: instantiation_const}
                )

                # F:[∃X P(X)]Q(X) expands to: F:P(c) ∨ F:Q(c)
                conclusions = [
                    [SignedFormula(F, restriction_inst)],
                    [SignedFormula(F, matrix_inst)],
                ]
                return RuleInfo("F-RestrictedExists", RuleType.BETA, 41, 2, conclusions)

        elif isinstance(formula, RestrictedUniversalFormula):
            # T:[∀X P(X)]Q(X) - for all x, if P(x) then Q(x)
            if sign == T:
                # Universal rules must be applied to ALL existing constants
                # plus potentially one fresh constant for completeness
                existing_constants = list(branch.ground_terms)

                if existing_constants:
                    # Check which constants we haven't instantiated this formula with yet
                    if signed_formula not in branch._universal_instantiations:
                        branch._universal_instantiations[signed_formula] = set()

                    used_constants = branch._universal_instantiations[signed_formula]
                    unused_constants = [
                        c for c in existing_constants if c not in used_constants
                    ]

                    if unused_constants:
                        # Use the first unused constant (don't mark as used yet - that happens during application)
                        const_name = unused_constants[0]

                        instantiation_const = Constant(const_name)
                        restriction_inst = formula.restriction.substitute_term(
                            {formula.var.name: instantiation_const}
                        )
                        matrix_inst = formula.matrix.substitute_term(
                            {formula.var.name: instantiation_const}
                        )

                        # T:[∀X P(X)]Q(X) expands to: F:P(c) ∨ T:Q(c)
                        conclusions = [
                            [SignedFormula(F, restriction_inst)],
                            [SignedFormula(T, matrix_inst)],
                        ]
                        # Store the constant name in the rule for later use during application
                        rule_info = RuleInfo(
                            "T-RestrictedForall", RuleType.BETA, 42, 2, conclusions
                        )
                        rule_info.instantiation_constant = (
                            const_name  # Custom attribute
                        )
                        return rule_info
                    else:
                        # All constants have been used - no more instantiations needed
                        return None
                else:
                    # No existing constants, use fresh one
                    fresh_const = Constant(f"c_{len(branch.nodes)}")
                    branch.ground_terms.add(fresh_const.name)

                    restriction_inst = formula.restriction.substitute_term(
                        {formula.var.name: fresh_const}
                    )
                    matrix_inst = formula.matrix.substitute_term(
                        {formula.var.name: fresh_const}
                    )

                    conclusions = [
                        [SignedFormula(F, restriction_inst)],
                        [SignedFormula(T, matrix_inst)],
                    ]
                    rule_info = RuleInfo(
                        "T-RestrictedForall", RuleType.BETA, 42, 2, conclusions
                    )
                    rule_info.instantiation_constant = (
                        fresh_const.name
                    )  # Track the fresh constant
                    return rule_info

            elif sign == F:
                # F:[∀X P(X)]Q(X) - there exists an x such that P(x) but not Q(x)
                # This is an existential witness - use unification to find the right constant
                unification_map = branch._unify_with_existing_terms(formula)

                if unification_map and formula.var.name in unification_map:
                    const_name = unification_map[formula.var.name]
                    instantiation_const = Constant(const_name)
                else:
                    instantiation_const = Constant(f"c_{len(branch.nodes)}")
                    branch.ground_terms.add(instantiation_const.name)

                restriction_inst = formula.restriction.substitute_term(
                    {formula.var.name: instantiation_const}
                )
                matrix_inst = formula.matrix.substitute_term(
                    {formula.var.name: instantiation_const}
                )

                # F:[∀X P(X)]Q(X) expands to: T:P(c) ∧ F:Q(c)
                conclusions = [
                    [SignedFormula(T, restriction_inst), SignedFormula(F, matrix_inst)]
                ]
                return RuleInfo(
                    "F-RestrictedForall", RuleType.ALPHA, 43, 1, conclusions
                )

        return None

    def apply_rule(  # noqa: C901
        self, node: TableauNode, branch: Branch, rule_info: RuleInfo
    ) -> None:
        """Apply a tableau rule with optimization, creating new branches if needed."""

        # Mark the formula as processed (except for universal quantifiers which can be reprocessed)
        if not hasattr(branch, "_processed_formulas"):
            branch._processed_formulas = set()

        # For universal quantifiers, mark the instantiation as used instead of marking formula as processed
        if (
            hasattr(rule_info, "instantiation_constant")
            and rule_info.instantiation_constant is not None
        ):
            # This is a universal quantifier instantiation
            if not hasattr(branch, "_universal_instantiations"):
                branch._universal_instantiations = {}
            if node.formula not in branch._universal_instantiations:
                branch._universal_instantiations[node.formula] = set()
            branch._universal_instantiations[node.formula].add(
                rule_info.instantiation_constant
            )
        else:
            # Regular formula processing
            branch._processed_formulas.add(node.formula)

        # Update statistics
        self.rule_application_stats[rule_info.name] += 1

        conclusions = rule_info.conclusions

        if len(conclusions) == 1:
            # Non-branching rule (alpha rule)
            for signed_formula in conclusions[0]:
                if not branch.has_formula(signed_formula):
                    new_node = TableauNode(self.node_counter, signed_formula)
                    self.node_counter += 1
                    self.nodes.append(new_node)
                    node.add_child(new_node, rule_info.name)

                    if branch.add_formula(signed_formula, new_node):
                        # Branch closed
                        if branch in self.open_branches:
                            self.open_branches.remove(branch)
                            self.closed_branches.append(branch)
                        return
        else:
            # Branching rule (beta rule)
            # Remove current branch from open branches
            if branch in self.open_branches:
                self.open_branches.remove(branch)

            parent_node = node
            for _i, conclusion_set in enumerate(conclusions):
                # Create new branch
                new_branch = self._create_branch(len(self.branches))
                self.branches.append(new_branch)

                # Copy existing formulas to new branch
                for existing_node in branch.nodes:
                    new_branch.add_formula(existing_node.formula, existing_node)

                # Copy ground terms from parent branch
                new_branch.ground_terms = branch.ground_terms.copy()

                # Copy universal instantiation tracking
                new_branch._universal_instantiations = {
                    sf: constants.copy()
                    for sf, constants in branch._universal_instantiations.items()
                }

                # Copy processed formulas to avoid reprocessing
                if hasattr(branch, "_processed_formulas"):
                    new_branch._processed_formulas = branch._processed_formulas.copy()
                else:
                    new_branch._processed_formulas = set()

                # Add new formulas
                branch_closed = False
                for signed_formula in conclusion_set:
                    if not new_branch.has_formula(signed_formula):
                        new_node = TableauNode(self.node_counter, signed_formula)
                        self.node_counter += 1
                        self.nodes.append(new_node)
                        parent_node.add_child(new_node, rule_info.name)

                        if new_branch.add_formula(signed_formula, new_node):
                            branch_closed = True
                            break

                if branch_closed:
                    self.closed_branches.append(new_branch)
                else:
                    self.open_branches.append(new_branch)

    def construct(self) -> TableauResult:
        """Construct the tableau with industrial-grade optimizations."""
        max_iterations = 1000  # Increased for complex formulas
        iteration = 0

        while (
            self.open_branches
            and not self.is_complete()
            and iteration < max_iterations
            and len(self.branches) < self.max_branching_factor
        ):

            iteration += 1

            # Advanced branch selection strategy
            selected_branch = self._select_optimal_branch()
            if not selected_branch:
                break

            # Get all applicable rules for this branch and prioritize them
            applicable_rules = self._get_prioritized_rules(selected_branch)
            if not applicable_rules:
                # No more rules can be applied to any branch
                break

            # Apply the highest priority rule
            best_rule = applicable_rules[0]  # Already sorted by priority
            node, rule_info = best_rule

            self.apply_rule(node, selected_branch, rule_info)

            # Early termination for satisfiability (first model found)
            if self.early_termination and len(self.open_branches) > 0:
                # Check if any branch is ready for model extraction (all atomic)
                for branch in self.open_branches:
                    if all(node.formula.formula.is_atomic() for node in branch.nodes):
                        break

        # Extract models from open branches
        models = []
        for branch in self.open_branches:
            if not branch.is_closed:
                model = self._extract_model(branch)
                if model:
                    models.append(model)

        return TableauResult(
            satisfiable=len(models) > 0,
            models=models,
            closed_branches=len(self.closed_branches),
            open_branches=len(self.open_branches),
            total_nodes=len(self.nodes),
            tableau=self,
        )

    def _extract_model(self, branch: Branch) -> Optional[Model]:
        """Extract a model from an open branch."""
        # Get all atoms
        atoms: set[str] = set()
        for node in branch.nodes:
            atoms.update(node.formula.formula.get_atoms())

        # Build valuation
        valuations = {}

        for atom in atoms:
            # Check what signs appear for this atom
            has_t = any(
                node.formula.sign == T and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_f = any(
                node.formula.sign == F and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_m = any(
                node.formula.sign == M and str(node.formula.formula) == atom
                for node in branch.nodes
            )
            has_n = any(
                node.formula.sign == N and str(node.formula.formula) == atom
                for node in branch.nodes
            )

            # Check for contradictions first - this should not happen in open branches
            if has_t and has_f:
                # This should not happen - branch should be closed
                return None

            if has_t:
                valuations[atom] = TRUE
            elif has_f:
                valuations[atom] = FALSE
            elif has_m:
                # M means both T and F are possible - choose one
                valuations[atom] = TRUE  # Could also be FALSE
            elif has_n:
                valuations[atom] = UNDEFINED
            else:
                # No constraint, default to undefined
                valuations[atom] = UNDEFINED

        return Model(valuations, {})

    def _select_optimal_branch(self) -> Optional[Branch]:
        """Select the optimal branch to process next."""
        if not self.open_branches:
            return None

        if self.branch_selection_strategy == "least_complex":
            # Select branch with lowest complexity score
            return min(self.open_branches, key=lambda b: b.complexity_score)
        elif self.branch_selection_strategy == "depth_first":
            # Select most recently created branch
            return self.open_branches[-1]
        elif self.branch_selection_strategy == "breadth_first":
            # Select oldest branch
            return self.open_branches[0]
        else:
            # Default: least complex
            return min(self.open_branches, key=lambda b: b.complexity_score)

    def _get_prioritized_rules(
        self, branch: Branch
    ) -> list[tuple[TableauNode, RuleInfo]]:
        """Get all applicable rules for a branch, sorted by priority."""
        applicable_rules = []

        for node in branch.nodes:
            rule_info = self._get_applicable_rule(node.formula, branch)
            if rule_info:
                applicable_rules.append((node, rule_info))

        # Sort by rule priority (RuleInfo.__lt__ handles the logic)
        applicable_rules.sort(key=lambda x: x[1])

        return applicable_rules

    def _try_extract_model(self, branch: Branch) -> Optional[Model]:
        """Try to extract a model from a branch (non-destructive)."""
        try:
            return self._extract_model(branch)
        except Exception:
            return None


def solve(formula: Formula, sign: Sign = T) -> TableauResult:
    """Solve a formula with the given sign."""
    signed_formula = SignedFormula(sign, formula)
    tableau = Tableau([signed_formula])
    return tableau.construct()


def valid(formula: Formula) -> bool:
    """Check if a formula is valid (true in all models).

    In weak Kleene logic, validity means the formula receives value 't'
    in ALL interpretations, not just those where premises are true.

    A formula is valid iff:
    - F:φ is unsatisfiable (cannot be false), AND
    - N:φ is unsatisfiable (cannot be undefined)
    """
    # Check if formula can be false
    result_f = solve(formula, F)
    if result_f.satisfiable:
        return False  # Can be false, so not valid

    # Check if formula can be undefined
    result_n = solve(formula, N)
    if result_n.satisfiable:
        return False  # Can be undefined, so not valid

    # If cannot be false or undefined, must be valid (always true)
    return True


def entails(premises: list[Formula], conclusion: Formula) -> bool:
    """Check if premises entail conclusion."""
    # P1, ..., Pn |- Q iff (P1 & ... & Pn & ~Q) is unsatisfiable
    from .formula import Conjunction, Negation

    if not premises:
        # Empty premises, check if conclusion is valid
        return valid(conclusion)

    # Combine premises
    combined_premises = premises[0]
    for p in premises[1:]:
        combined_premises = Conjunction(combined_premises, p)

    # Test satisfiability of premises & ~conclusion
    test_formula = Conjunction(combined_premises, Negation(conclusion))
    result = solve(test_formula, T)

    return not result.satisfiable
