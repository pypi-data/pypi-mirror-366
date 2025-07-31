#!/usr/bin/env python3
"""
wKrQ Basic Examples

Demonstrates basic usage of the wKrQ logic system.
"""

from wkrq import Formula, solve, valid, entails, parse, parse_inference, test_inference, T, F, M, N

def basic_formulas():
    """Demonstrate basic formula construction."""
    print("=== Basic Formula Construction ===")
    
    # Create atoms
    p, q, r = Formula.atoms("p", "q", "r")
    print(f"Atoms: {p}, {q}, {r}")
    
    # Build complex formulas using operators
    conjunction = p & q
    disjunction = p | q
    negation = ~p
    implication = p.implies(q)
    
    print(f"Conjunction: {conjunction}")
    print(f"Disjunction: {disjunction}")
    print(f"Negation: {negation}")
    print(f"Implication: {implication}")
    
    # Complex formula
    complex_formula = (p & q) | (~p & r)
    print(f"Complex formula: {complex_formula}")
    print()


def satisfiability_testing():
    """Demonstrate satisfiability testing."""
    print("=== Satisfiability Testing ===")
    
    p = Formula.atom("p")
    
    # Satisfiable formula
    satisfiable = p | ~p
    result = solve(satisfiable, T)
    print(f"Formula: {satisfiable}")
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models: {result.models}")
    print()
    
    # Unsatisfiable formula
    unsatisfiable = p & ~p
    result = solve(unsatisfiable, T)
    print(f"Formula: {unsatisfiable}")
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models: {result.models}")
    print()


def different_signs():
    """Demonstrate different signs in wKrQ."""
    print("=== Different Signs ===")
    
    p = Formula.atom("p")
    formula = p | ~p
    
    for sign in [T, F, M, N]:
        result = solve(formula, sign)
        print(f"Sign {sign}: {formula} → Satisfiable: {result.satisfiable}")
    print()


def validity_testing():
    """Demonstrate validity testing."""
    print("=== Validity Testing ===")
    
    p, q = Formula.atoms("p", "q")
    
    # Tautology in weak Kleene logic
    tautology = p | ~p
    print(f"Formula: {tautology}")
    print(f"Valid: {valid(tautology)}")
    
    # Non-tautology
    contingent = p & q
    print(f"Formula: {contingent}")
    print(f"Valid: {valid(contingent)}")
    print()


def inference_testing():
    """Demonstrate inference testing."""
    print("=== Inference Testing ===")
    
    # Valid inferences
    valid_inferences = [
        "p, p -> q |- q",           # Modus ponens
        "p -> q, ~q |- ~p",         # Modus tollens
        "p | q, ~p |- q",           # Disjunctive syllogism
        "p -> q, q -> r |- p -> r", # Hypothetical syllogism
    ]
    
    for inf_str in valid_inferences:
        inference = parse_inference(inf_str)
        result = test_inference(inference)
        status = "✓" if result.valid else "✗"
        print(f"{status} {inf_str}")
    
    print()
    
    # Invalid inferences
    invalid_inferences = [
        "p |- q",                   # No connection
        "p -> q |- q",             # Affirming the consequent
        "p -> q, ~p |- ~q",        # Denying the antecedent
    ]
    
    for inf_str in invalid_inferences:
        inference = parse_inference(inf_str)
        result = test_inference(inference)
        status = "✓" if result.valid else "✗"
        print(f"{status} {inf_str}")
        if not result.valid and result.countermodels:
            print(f"    Countermodel: {result.countermodels[0]}")
    print()


def parsing_examples():
    """Demonstrate formula parsing."""
    print("=== Formula Parsing ===")
    
    formulas = [
        "p",
        "p & q",
        "p | q",
        "~p",
        "p -> q",
        "(p & q) | r",
        "p -> (q -> r)",
        "~(p & q)",
    ]
    
    for formula_str in formulas:
        formula = parse(formula_str)
        print(f"'{formula_str}' → {formula}")
    print()


def weak_kleene_examples():
    """Demonstrate weak Kleene logic specifics."""
    print("=== Weak Kleene Logic Examples ===")
    
    p, q = Formula.atoms("p", "q")
    
    # In weak Kleene logic, these behave differently than classical logic
    test_formulas = [
        p | ~p,              # Still a tautology
        p & ~p,              # Still unsatisfiable  
        p | q,               # Can have undefined values
        p & q,               # Can have undefined values
    ]
    
    for formula in test_formulas:
        result = solve(formula, T)
        print(f"T: {formula}")
        print(f"  Satisfiable: {result.satisfiable}")
        if result.models:
            print(f"  Sample model: {result.models[0]}")
        print()


def first_order_examples():
    """Demonstrate first-order logic features."""
    print("=== First-Order Logic Examples ===")
    
    # Create terms
    x = Formula.variable("X")
    a = Formula.constant("a")
    b = Formula.constant("b")
    
    # Create predicates
    p_x = Formula.predicate("P", [x])
    p_a = Formula.predicate("P", [a])
    q_a = Formula.predicate("Q", [a])
    r_ab = Formula.predicate("R", [a, b])
    
    print(f"Variable: {x}")
    print(f"Constants: {a}, {b}")
    print(f"Predicates: {p_x}, {p_a}, {q_a}, {r_ab}")
    
    # Test predicate satisfiability
    result = solve(p_a, T)
    print(f"T: {p_a} → Satisfiable: {result.satisfiable}")
    
    # Test predicate contradiction
    contradiction = p_a & ~p_a
    result = solve(contradiction, T)
    print(f"T: {contradiction} → Satisfiable: {result.satisfiable}")
    
    # Restricted quantifiers (construction only - tableau rules not yet implemented)
    student_x = Formula.predicate("Student", [x])
    human_x = Formula.predicate("Human", [x])
    
    exists = Formula.restricted_exists(x, student_x, human_x)
    forall = Formula.restricted_forall(x, student_x, human_x)
    
    print(f"Restricted existential: {exists}")
    print(f"Restricted universal: {forall}")
    print()


def main():
    """Run all examples."""
    print("wKrQ Logic System Examples")
    print("=" * 50)
    print()
    
    basic_formulas()
    satisfiability_testing()
    different_signs()
    validity_testing()
    inference_testing()
    parsing_examples()
    weak_kleene_examples()
    first_order_examples()
    
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()