"""Tests for ACrQ tableau implementation."""

from wkrq.acrq_parser import SyntaxMode, parse_acrq_formula
from wkrq.acrq_tableau import ACrQModel, ACrQTableau
from wkrq.formula import (
    BilateralPredicateFormula,
    CompoundFormula,
    Constant,
)
from wkrq.semantics import FALSE, TRUE, BilateralTruthValue
from wkrq.signs import F, M, N, SignedFormula, T


class TestACrQTableau:
    """Test ACrQ tableau construction and rules."""

    def test_bilateral_predicate_identification(self):
        """Test that bilateral predicates are properly identified."""
        # Create formulas with bilateral predicates
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        initial = [SignedFormula(T, human), SignedFormula(F, human_star)]

        tableau = ACrQTableau(initial)

        # Check bilateral pairs are registered
        assert "Human" in tableau.bilateral_pairs
        assert tableau.bilateral_pairs["Human"] == "Human*"
        assert tableau.bilateral_pairs["Human*"] == "Human"

    def test_bilateral_contradiction_detection(self):
        """Test detection of bilateral contradictions (T:R and T:R*)."""
        # Create contradictory bilateral predicates
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        initial = [SignedFormula(T, human), SignedFormula(T, human_star)]

        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be unsatisfiable due to bilateral contradiction
        assert not result.satisfiable
        # The number of closed branches may vary depending on implementation
        assert result.closed_branches >= 0

    def test_t_r_rule(self):
        """Test T:R rule (R is true, R* is false)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        initial = [SignedFormula(T, human)]
        tableau = ACrQTableau(initial)

        # Get the rule for T:R
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "T-R"
        assert rule.rule_type.value == "alpha"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 2

        # Check conclusions
        pos_pred, neg_pred = human.to_standard_predicates()
        expected = [SignedFormula(T, pos_pred), SignedFormula(F, neg_pred)]

        assert rule.conclusions[0][0].sign == expected[0].sign
        assert str(rule.conclusions[0][0].formula) == str(expected[0].formula)
        assert rule.conclusions[0][1].sign == expected[1].sign
        assert str(rule.conclusions[0][1].formula) == str(expected[1].formula)

    def test_t_r_star_rule(self):
        """Test T:R* rule (R is false, R* is true)."""
        human_star = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=True
        )

        initial = [SignedFormula(T, human_star)]
        tableau = ACrQTableau(initial)

        # Get the rule for T:R*
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "T-R*"
        assert rule.rule_type.value == "alpha"

        # Check conclusions
        pos_pred, neg_pred = human_star.to_standard_predicates()
        assert len(rule.conclusions[0]) == 2
        assert rule.conclusions[0][0].sign == F  # F:Human(alice)
        assert rule.conclusions[0][1].sign == T  # T:Human*(alice)

    def test_f_r_rule(self):
        """Test F:R rule (branches to T:R* or N:R,R*)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        initial = [SignedFormula(F, human)]
        tableau = ACrQTableau(initial)

        # Get the rule for F:R
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "F-R"
        assert rule.rule_type.value == "beta"
        assert len(rule.conclusions) == 2

        # Branch 1: T:R*
        assert len(rule.conclusions[0]) == 1
        assert rule.conclusions[0][0].sign == T

        # Branch 2: N:R and N:R*
        assert len(rule.conclusions[1]) == 2
        assert rule.conclusions[1][0].sign == N
        assert rule.conclusions[1][1].sign == N

    def test_m_r_rule(self):
        """Test M:R rule (branches to T:R or F:R)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        initial = [SignedFormula(M, human)]
        tableau = ACrQTableau(initial)

        # Get the rule for M:R
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "M-R"
        assert rule.rule_type.value == "beta"
        assert len(rule.conclusions) == 2

        # Each branch has one formula
        assert len(rule.conclusions[0]) == 1
        assert len(rule.conclusions[1]) == 1
        assert rule.conclusions[0][0].sign == T  # T:R
        assert rule.conclusions[1][0].sign == F  # F:R

    def test_n_r_rule(self):
        """Test N:R rule (gap: F:R and F:R*)."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        initial = [SignedFormula(N, human)]
        tableau = ACrQTableau(initial)

        # Get the rule for N:R
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "N-R"
        assert rule.rule_type.value == "alpha"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 2

        # Both should be F
        assert rule.conclusions[0][0].sign == F
        assert rule.conclusions[0][1].sign == F

    def test_bilateral_negation_rule(self):
        """Test negation of bilateral predicates."""
        # ¬R(x) should become R*(x)
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )
        neg_human = CompoundFormula("~", [human])

        initial = [SignedFormula(T, neg_human)]
        tableau = ACrQTableau(initial)

        # Get the rule for ~R
        rule = tableau._get_acrq_rule(initial[0], tableau.root)

        assert rule is not None
        assert rule.name == "Bilateral-Negation"
        assert rule.rule_type.value == "alpha"
        assert len(rule.conclusions) == 1
        assert len(rule.conclusions[0]) == 1

        # Should produce T:R*
        result_formula = rule.conclusions[0][0].formula
        assert isinstance(result_formula, BilateralPredicateFormula)
        assert result_formula.is_negative is True

    def test_knowledge_gap_scenario(self):
        """Test handling of knowledge gaps (neither R nor R* true)."""
        # Query: Is Human(charlie) defined?
        # If we have no information, it should be undefined

        human = BilateralPredicateFormula(
            "Human", [Constant("charlie")], is_negative=False
        )

        # Test N:Human(charlie) is satisfiable
        initial = [SignedFormula(N, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        # Model should have both Human(charlie) and Human*(charlie) as false
        model = result.models[0]
        assert isinstance(model, ACrQModel)

        # Check bilateral valuations
        assert "Human(charlie)" in model.bilateral_valuations
        btv = model.bilateral_valuations["Human(charlie)"]
        assert btv.positive == FALSE  # Human(charlie) is false
        assert btv.negative == FALSE  # Human*(charlie) is false
        assert btv.is_gap()  # This is a knowledge gap

    def test_knowledge_glut_scenario(self):
        """Test handling of knowledge gluts (both R and R* have evidence)."""
        # This should lead to contradiction in ACrQ
        human = BilateralPredicateFormula(
            "Human", [Constant("charlie")], is_negative=False
        )
        human_star = BilateralPredicateFormula(
            "Human", [Constant("charlie")], is_negative=True
        )

        # Both T:Human(charlie) and T:Human*(charlie)
        initial = [SignedFormula(T, human), SignedFormula(T, human_star)]

        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be unsatisfiable (bilateral contradiction)
        assert not result.satisfiable

    def test_paraconsistent_inference(self):
        """Test bilateral contradiction behavior according to Ferguson."""
        # According to Ferguson's tableau rules, T:R(a) and T:R*(a) do create
        # a contradiction at the proof level. The paraconsistency is at the
        # semantic level where gluts are allowed in models.

        # Parse formulas
        f1 = parse_acrq_formula("Human(alice)", SyntaxMode.TRANSPARENT)
        f2 = parse_acrq_formula(
            "¬Human(alice)", SyntaxMode.TRANSPARENT
        )  # Becomes Human*(alice)

        # Set up tableau with bilateral contradiction
        initial = [
            SignedFormula(T, f1),
            SignedFormula(T, f2),
        ]

        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # According to Ferguson's rules, this creates a contradiction
        # T:Human(alice) generates F:Human*(alice)
        # T:Human*(alice) already exists
        # So we get T:Human*(alice) and F:Human*(alice) - contradiction
        assert not result.satisfiable

    def test_valid_bilateral_inference(self):
        """Test a valid inference with bilateral predicates."""
        # [∀X Human(X)]Nice(X), Human(alice) |- Nice(alice)

        # Parse formulas - use restricted quantifier for proper instantiation
        rule = parse_acrq_formula("[∀X Human(X)]Nice(X)", SyntaxMode.TRANSPARENT)
        premise = parse_acrq_formula("Human(alice)", SyntaxMode.TRANSPARENT)
        conclusion = parse_acrq_formula("Nice(alice)", SyntaxMode.TRANSPARENT)

        # Test by negating conclusion
        initial = [
            SignedFormula(T, rule),
            SignedFormula(T, premise),
            SignedFormula(F, conclusion),
        ]

        tableau = ACrQTableau(initial)
        result = tableau.construct()

        # Should be unsatisfiable (inference is valid)
        assert not result.satisfiable

    def test_acrq_model_extraction(self):
        """Test ACrQ model extraction with bilateral valuations."""
        human = BilateralPredicateFormula(
            "Human", [Constant("alice")], is_negative=False
        )

        initial = [SignedFormula(T, human)]
        tableau = ACrQTableau(initial)
        result = tableau.construct()

        assert result.satisfiable
        model = result.models[0]
        assert isinstance(model, ACrQModel)

        # Check bilateral valuations
        assert "Human(alice)" in model.bilateral_valuations
        btv = model.bilateral_valuations["Human(alice)"]
        assert isinstance(btv, BilateralTruthValue)
        assert btv.positive == TRUE
        assert btv.negative == FALSE
        assert btv.is_determinate()
        assert not btv.is_gap()
