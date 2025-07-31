#!/usr/bin/env python3
"""
Quick start examples for wKrQ - Three-valued weak Kleene logic.

This file demonstrates basic usage of the wKrQ package.
"""

from wkrq import Formula, solve, valid, entails, T, F, M, N

def basic_examples():
    """Basic propositional logic examples."""
    print("=== Basic Propositional Logic ===\n")
    
    # Create atomic formulas
    p, q, r = Formula.atoms('p', 'q', 'r')
    
    # Build compound formulas
    formula1 = p & q
    formula2 = p | ~p
    formula3 = p.implies(q)
    
    print(f"Formula 1: {formula1}")
    print(f"Formula 2: {formula2}")
    print(f"Formula 3: {formula3}")
    
    # Test satisfiability
    result = solve(formula1, T)
    print(f"\n{formula1} is satisfiable: {result.satisfiable}")
    print(f"Models: {result.models}")
    
    # Test validity
    print(f"\n{formula2} is valid: {valid(formula2)}")
    
    # Test entailment
    premises = [p, p.implies(q)]
    conclusion = q
    print(f"\nModus ponens ({premises} |- {conclusion}): {entails(premises, conclusion)}")


def three_valued_examples():
    """Examples showcasing three-valued logic."""
    print("\n\n=== Three-Valued Logic ===\n")
    
    p = Formula.atom('p')
    
    # Test with different signs
    print("Testing formula 'p' with different signs:")
    for sign, name in [(T, "true"), (F, "false"), (M, "multiple"), (N, "neither/undefined")]:
        result = solve(p, sign)
        print(f"  Sign {sign} ({name}): satisfiable = {result.satisfiable}")
        if result.models:
            print(f"    Model: {result.models[0]}")
    
    # Law of excluded middle in three-valued logic
    lem = p | ~p
    print(f"\nLaw of excluded middle '{lem}':")
    print(f"  Can be true: {solve(lem, T).satisfiable}")
    print(f"  Can be undefined: {solve(lem, N).satisfiable}")
    
    # Contradiction in three-valued logic
    contradiction = p & ~p
    print(f"\nContradiction '{contradiction}':")
    print(f"  Can be true: {solve(contradiction, T).satisfiable}")
    print(f"  Can be undefined: {solve(contradiction, N).satisfiable}")


def first_order_examples():
    """First-order logic with restricted quantification."""
    print("\n\n=== First-Order Logic ===\n")
    
    # Variables and constants
    x = Formula.variable('X')
    socrates = Formula.constant('socrates')
    
    # Predicates
    human = Formula.predicate('Human', [x])
    mortal = Formula.predicate('Mortal', [x])
    human_socrates = Formula.predicate('Human', [socrates])
    
    # Restricted quantification
    all_humans_mortal = Formula.restricted_forall(x, human, mortal)
    exists_human = Formula.restricted_exists(x, human, human)
    
    print(f"Universal: {all_humans_mortal}")
    print(f"Existential: {exists_human}")
    
    # Classical syllogism
    premises = all_humans_mortal & human_socrates
    result = solve(premises, T)
    print(f"\nPremises satisfiable: {result.satisfiable}")
    print(f"Number of models: {len(result.models)}")


def philosophical_example():
    """Philosophical application: Sorites paradox."""
    print("\n\n=== Philosophical Application: Sorites Paradox ===\n")
    
    # Model vague predicates
    heap_1000 = Formula.atom('Heap1000')
    heap_999 = Formula.atom('Heap999')
    heap_1 = Formula.atom('Heap1')
    
    # Clear cases
    print("Clear cases:")
    print(f"  1000 grains is a heap: {solve(heap_1000, T).satisfiable}")
    print(f"  1 grain is not a heap: {solve(heap_1, F).satisfiable}")
    
    # Borderline case with three-valued logic
    print("\nBorderline case (999 grains):")
    print(f"  Can be true: {solve(heap_999, T).satisfiable}")
    print(f"  Can be false: {solve(heap_999, F).satisfiable}")
    print(f"  Can be undefined: {solve(heap_999, N).satisfiable}")
    
    # Sorites principle
    sorites_step = heap_1000.implies(heap_999)
    paradox = heap_1000 & sorites_step & ~heap_1
    
    print(f"\nSorites paradox: {paradox}")
    result = solve(paradox, T)
    print(f"Paradox is satisfiable: {result.satisfiable}")
    
    if result.satisfiable and result.models:
        model = result.models[0]
        print("\nResolution via three-valued logic:")
        print(f"  Heap(1000) = {model.valuations.get('Heap1000', 'undefined')}")
        print(f"  Heap(999) = {model.valuations.get('Heap999', 'undefined')}")
        print(f"  Heap(1) = {model.valuations.get('Heap1', 'undefined')}")


if __name__ == "__main__":
    basic_examples()
    three_valued_examples()
    first_order_examples()
    philosophical_example()
    
    print("\n\nFor more examples, see the documentation at:")
    print("https://github.com/bradleypallen/wkrq/tree/main/docs")