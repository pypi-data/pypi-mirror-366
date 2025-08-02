#!/usr/bin/env python3
"""
Philosophical Examples for wKrQ Tableau System

This file contains compelling examples that demonstrate the wKrQ tableau system's
capabilities across different philosophical and logical contexts, showcasing how
the three-valued weak Kleene logic with restricted quantification handles
reasoning under uncertainty and vagueness.
"""

from wkrq import Formula, solve, valid, entails, parse, T, F, M, N
from wkrq.semantics import TRUE, FALSE, UNDEFINED


def example_1_classical_vs_nonclassical():
    """
    Example 1: Classical vs Non-Classical Reasoning
    
    Demonstrates how wKrQ handles formulas that behave differently 
    in classical vs many-valued logic systems.
    """
    print("=" * 60)
    print("EXAMPLE 1: CLASSICAL VS NON-CLASSICAL REASONING")
    print("=" * 60)
    
    # Law of Excluded Middle: p ∨ ¬p
    p = Formula.atom("p")
    lem = p | ~p
    
    print(f"Formula: {lem}")
    print("Question: Is the Law of Excluded Middle valid in wKrQ?")
    
    # Check validity
    is_valid = valid(lem)
    print(f"Valid in wKrQ: {is_valid}")
    
    # Find models to understand why/why not
    result = solve(lem, T)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Number of models: {len(result.models)}")
    
    if result.models:
        print("Models found:")
        for i, model in enumerate(result.models, 1):
            print(f"  Model {i}: {model}")
    
    print("\nAnalysis:")
    print("In classical logic, p ∨ ¬p is always true (tautology).")
    print("In wKrQ, this formula is valid because weak Kleene logic")
    print("preserves classical tautologies, even with three truth values.")
    print()


def example_2_sorites_paradox():
    """
    Example 2: The Sorites Paradox
    
    Shows how wKrQ's three-valued logic can model vague predicates
    and handle the famous sorites paradox about heap of sand.
    """
    print("=" * 60)
    print("EXAMPLE 2: THE SORITES PARADOX")
    print("=" * 60)
    
    # Predicates for the sorites paradox
    # H1000 = "1000 grains form a heap"
    # H999 = "999 grains form a heap" 
    # etc.
    
    h1000 = Formula.atom("H1000")  # 1000 grains is clearly a heap
    h999 = Formula.atom("H999")    # 999 grains - still a heap?
    h1 = Formula.atom("H1")        # 1 grain is clearly not a heap
    
    print("Sorites Paradox Setup:")
    print("H1000: '1000 grains form a heap' (clearly true)")  
    print("H1: '1 grain forms a heap' (clearly false)")
    print("H999: '999 grains form a heap' (borderline case)")
    
    # Sorites principle: if n grains form a heap, then n-1 grains form a heap
    sorites_step = h1000.implies(h999)
    print(f"\nSorites step: {sorites_step}")
    
    # The paradox: combining clear cases with sorites principle
    premises = [h1000, sorites_step, ~h1]
    combined = premises[0] & premises[1] & premises[2]
    
    print(f"Combined premises: H1000 ∧ (H1000 → H999) ∧ ¬H1")
    
    # Check satisfiability
    result = solve(combined, T)
    print(f"Satisfiable: {result.satisfiable}")
    
    if result.satisfiable:
        print("Models found:")
        for model in result.models:
            print(f"  {model}")
            h1000_val = model.valuations.get("H1000", UNDEFINED)
            h999_val = model.valuations.get("H999", UNDEFINED)  
            h1_val = model.valuations.get("H1", UNDEFINED)
            
            print(f"    H1000 = {h1000_val}, H999 = {h999_val}, H1 = {h1_val}")
    
    print("\nAnalysis:")
    print("wKrQ allows for borderline cases where H999 might be undefined,")
    print("avoiding the classical paradox while preserving clear cases.")
    print()


def example_3_tableau_signs_and_semantics():
    """
    Example 3: Tableau Signs and Three-Valued Semantics
    
    Demonstrates the four tableau signs T, F, M, N and how they relate
    to the three truth values in weak Kleene logic: t (true), f (false), e (undefined).
    """
    print("=" * 60)
    print("EXAMPLE 3: TABLEAU SIGNS AND THREE-VALUED SEMANTICS") 
    print("=" * 60)
    
    rain = Formula.atom("Rain")
    
    print("Tableau Signs in wKrQ:")
    print("T: 'True' - formula must have truth value t (true)")
    print("F: 'False' - formula must have truth value f (false)")  
    print("M: 'Multiple' - formula can have truth values t or f")
    print("N: 'Neither' - formula must have truth value e (undefined)")
    print()
    print("These signs are proof-theoretic tools, not epistemic operators.")
    print("They help construct tableaux for the three-valued semantics.")
    print()
    
    # Test each sign
    for sign, description in [(T, "true"), (F, "false"), 
                             (M, "true or false"), (N, "undefined")]:
        print(f"Testing: Rain must be {description} (sign {sign})")
        result = solve(rain, sign)
        print(f"  Satisfiable: {result.satisfiable}")
        if result.models:
            model = result.models[0]
            rain_val = model.valuations.get("Rain", UNDEFINED)
            print(f"  Rain gets truth value: {rain_val}")
        print()
    
    # Sign T and F are contradictory
    print("Note: Signs T and F are contradictory in tableau construction.")
    print("A formula cannot simultaneously be required to be true and false.")
    print()


def example_4_restricted_quantifiers():
    """
    Example 4: Restricted Quantifiers in First-Order Logic
    
    Shows wKrQ's restricted quantifier reasoning with concrete examples
    from philosophical logic about properties and domains.
    """
    print("=" * 60)
    print("EXAMPLE 4: RESTRICTED QUANTIFIERS")
    print("=" * 60)
    
    # Variables and predicates for restricted quantification
    x = Formula.variable("X")
    student_x = Formula.predicate("Student", [x])
    human_x = Formula.predicate("Human", [x]) 
    mortal_x = Formula.predicate("Mortal", [x])
    
    # Restricted existential: [∃X Student(X)]Human(X)
    # "There exists something that is both a student and human"
    restricted_exists = Formula.restricted_exists(x, student_x, human_x)
    print(f"Restricted existential: {restricted_exists}")
    print("Meaning: 'There exists an X such that X is a student and X is human'")
    
    result = solve(restricted_exists, T)
    print(f"Satisfiable: {result.satisfiable}")
    if result.satisfiable:
        print("This is satisfiable - we can have student-humans.")
    print()
    
    # Restricted universal: [∀X Human(X)]Mortal(X)  
    # "All humans are mortal"
    restricted_forall = Formula.restricted_forall(x, human_x, mortal_x)
    print(f"Restricted universal: {restricted_forall}")
    print("Meaning: 'For all X, if X is human, then X is mortal'")
    
    result = solve(restricted_forall, T)
    print(f"Satisfiable: {result.satisfiable}")
    if result.satisfiable:
        print("This is satisfiable - it's a reasonable universal claim.")
    print()
    
    # Complex reasoning with both
    complex_formula = restricted_exists & restricted_forall
    print("Complex reasoning: Combine both restricted quantifiers")
    print("'There exist student-humans AND all humans are mortal'")
    
    result = solve(complex_formula, T)
    print(f"Combined formula satisfiable: {result.satisfiable}")
    print("This shows how wKrQ handles complex first-order reasoning.")
    print()


def example_5_nonmonotonic_reasoning():
    """
    Example 5: Nonmonotonic Reasoning Patterns
    
    Demonstrates how wKrQ can model defeasible reasoning and
    nonmonotonic inference patterns common in AI and philosophy.
    """
    print("=" * 60)
    print("EXAMPLE 5: NONMONOTONIC REASONING PATTERNS")
    print("=" * 60)
    
    # Typical case: Birds fly, penguins are birds, penguins don't fly
    bird = Formula.atom("Bird")
    flies = Formula.atom("Flies") 
    penguin = Formula.atom("Penguin")
    
    print("Nonmonotonic reasoning scenario:")
    print("- Typically, birds fly")
    print("- Penguins are birds") 
    print("- But penguins don't fly")
    print()
    
    # Default rule: Bird → Flies (defeasible)
    default_rule = bird.implies(flies)
    print(f"Default rule: {default_rule}")
    
    # Specific case: Penguin ∧ Bird ∧ ¬Flies
    penguin_case = penguin & bird & ~flies
    print(f"Penguin exception: {penguin_case}")
    
    # Test consistency of having both general rule and exception
    combined = default_rule & penguin_case
    print(f"Combined: {combined}")
    
    result = solve(combined, T)
    print(f"Can we have both the rule and the exception? {result.satisfiable}")
    
    if result.satisfiable:
        print("Models found:")
        for model in result.models:
            print(f"  {model}")
            
    print("\nAnalysis:")
    print("In classical logic, this might lead to contradiction.")
    print("In wKrQ, we can model the uncertainty and exceptions")
    print("that are natural in nonmonotonic reasoning.")
    print()


def example_6_three_valued_semantics():
    """
    Example 6: Three-Valued Semantics in Action
    
    Shows how wKrQ's three truth values (t, f, e) handle formulas
    that are problematic in classical two-valued logic.
    """
    print("=" * 60)
    print("EXAMPLE 6: THREE-VALUED SEMANTICS IN ACTION")
    print("=" * 60)
    
    # Create a formula involving undefined atomic proposition
    p = Formula.atom("BorderlineCase")
    
    print("Three truth values in weak Kleene logic:")
    print("t: true (classical truth)")
    print("f: false (classical falsity)")
    print("e: undefined (neither true nor false)")
    print()
    
    print("Testing how undefined values propagate:")
    
    # Test conjunction with undefined
    q = Formula.atom("DefinitelyTrue")
    conjunction = p & q
    
    print(f"Formula: {conjunction}")
    print("If BorderlineCase=e and DefinitelyTrue=t, what is the conjunction?")
    
    result = solve(conjunction, N)  # N sign for undefined result
    print(f"Can conjunction be undefined (N)? {result.satisfiable}")
    
    if result.satisfiable:
        model = result.models[0]
        print(f"Model: {model}")
    print()
    
    # Test disjunction with undefined
    disjunction = p | q
    print(f"Formula: {disjunction}")
    print("If BorderlineCase=e and DefinitelyTrue=t, what is the disjunction?")
    
    result_t = solve(disjunction, T)  # Should not be true
    result_n = solve(disjunction, N)  # Should be undefined
    
    print(f"Is disjunction true (T)? {result_t.satisfiable}")
    print(f"Is disjunction undefined (N)? {result_n.satisfiable}")
    print("In weak Kleene: t ∨ e = e (any undefined input → undefined output)")
    print()
    
    # Test negation of undefined
    negation = ~p
    print(f"Formula: {negation}")
    print("If BorderlineCase=e, what is ¬BorderlineCase?")
    
    result = solve(negation, N)
    print(f"Is negation undefined (N)? {result.satisfiable}")
    print("In weak Kleene: ¬e = e (undefined stays undefined)")
    print()


def example_7_practical_reasoning():
    """
    Example 7: Practical Reasoning and Decision Making
    
    Shows how wKrQ can model practical reasoning scenarios
    involving uncertainty, preferences, and decision-making.
    """
    print("=" * 60)
    print("EXAMPLE 7: PRACTICAL REASONING AND DECISION MAKING")
    print("=" * 60)
    
    # Decision scenario: Should I take an umbrella?
    will_rain = Formula.atom("WillRain")
    take_umbrella = Formula.atom("TakeUmbrella")
    stay_dry = Formula.atom("StayDry")
    
    print("Practical reasoning scenario: Should I take an umbrella?")
    print("Factors to consider:")
    print("- Will it rain? (uncertain)")
    print("- If I take umbrella and it rains, I stay dry")
    print("- If I don't take umbrella and it rains, I get wet")
    print()
    
    # Practical rules
    rule1 = (take_umbrella & will_rain).implies(stay_dry)
    rule2 = (~take_umbrella & will_rain).implies(~stay_dry)
    
    print(f"Rule 1: {rule1}")
    print(f"Rule 2: {rule2}")
    print()
    
    # Scenario 1: Uncertain about rain, decide to take umbrella
    scenario1 = rule1 & rule2 & take_umbrella
    print("Scenario 1: Take umbrella (regardless of rain uncertainty)")
    
    result1 = solve(scenario1, T)
    print(f"Satisfiable: {result1.satisfiable}")
    if result1.models:
        for model in result1.models:
            rain_val = model.valuations.get("WillRain", "unknown")
            dry_val = model.valuations.get("StayDry", "unknown")
            print(f"  Model: Rain={rain_val}, StayDry={dry_val}")
    print()
    
    # Scenario 2: Don't take umbrella
    scenario2 = rule1 & rule2 & ~take_umbrella
    print("Scenario 2: Don't take umbrella")
    
    result2 = solve(scenario2, T)
    print(f"Satisfiable: {result2.satisfiable}")
    if result2.models:
        for model in result2.models:
            rain_val = model.valuations.get("WillRain", "unknown")
            dry_val = model.valuations.get("StayDry", "unknown")
            print(f"  Model: Rain={rain_val}, StayDry={dry_val}")
    
    print("\nAnalysis:")
    print("wKrQ helps model decision-making under uncertainty,")
    print("showing the consequences of different choices.")
    print()


def main():
    """Run all philosophical examples."""
    print("PHILOSOPHICAL EXAMPLES FOR wKrQ TABLEAU SYSTEM")
    print("=" * 60)
    print("This demonstration shows how wKrQ's three-valued weak Kleene logic")
    print("with restricted quantification handles various philosophical and")
    print("practical reasoning scenarios.")
    print()
    
    example_1_classical_vs_nonclassical()
    example_2_sorites_paradox()
    example_3_tableau_signs_and_semantics()
    example_4_restricted_quantifiers()
    example_5_nonmonotonic_reasoning()
    example_6_three_valued_semantics()
    example_7_practical_reasoning()
    
    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("These examples demonstrate wKrQ's versatility in handling:")
    print("• Classical vs non-classical reasoning patterns")
    print("• Vagueness and borderline cases (sorites paradox)")
    print("• Three-valued semantics with undefined truth values")
    print("• First-order reasoning with restricted quantifiers")
    print("• Nonmonotonic and defeasible reasoning")
    print("• Practical decision-making under uncertainty")
    print()
    print("The three-valued weak Kleene logic (t, f, e) with four tableau")
    print("signs (T, F, M, N) provides a rich framework for philosophical")
    print("logic that handles uncertainty and vagueness naturally.")


if __name__ == "__main__":
    main()