# wKrQ API Reference

**Version:** 1.2.0  
**Date:** August 2025  
**Author:** Bradley P. Allen

The wKrQ Python API provides programmatic access to weak Kleene logic reasoning, tableau construction, and inference validation.

## Installation

```python
pip install wkrq
```

## Core Imports

```python
from wkrq import (
    # Core logic functions
    solve, valid, entails, check_inference,
    
    # Formula construction
    Formula, parse, parse_inference,
    
    # Signs system
    T, F, M, N, SignedFormula,
    
    # Advanced features
    Inference, TableauResult, Tableau
)

# Import semantic constants separately
from wkrq.semantics import TRUE, FALSE, UNDEFINED
```

## Basic Formula Testing

### Satisfiability Testing

Test if formulas can be satisfied under different signs:

```python
from wkrq import solve, parse, T, F, M, N

# Parse and test formula satisfiability
formula = parse("p & q")
result = solve(formula, T)  # Test under T sign

print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")
print(f"Total nodes: {result.total_nodes}")

# Test under different signs
for sign in [T, F, M, N]:
    result = solve(formula, sign)
    print(f"{sign}:(p & q) satisfiable: {result.satisfiable}")
```

### Validity Testing

Check if formulas are valid (true in all interpretations):

```python
from wkrq import valid, parse

# Classical tautology - NOT valid in weak Kleene
tautology = parse("p | ~p")
is_valid = valid(tautology)
print(f"p | ~p is valid: {is_valid}")  # False

# Test what signs are unsatisfiable
result_f = solve(tautology, F)
result_n = solve(tautology, N)
print(f"Can be false: {result_f.satisfiable}")      # False
print(f"Can be undefined: {result_n.satisfiable}")  # True
```

## Tableau Construction and Analysis

### Accessing Tableau Trees

```python
from wkrq import solve, parse, T
from wkrq.cli import TableauTreeRenderer

formula = parse("p -> q")
result = solve(formula, T)

if result.tableau:
    # Create renderer with rule display
    renderer = TableauTreeRenderer(show_rules=True)
    
    # Generate different formats
    ascii_tree = renderer.render_ascii(result.tableau)
    unicode_tree = renderer.render_unicode(result.tableau)
    json_data = renderer.render_json(result.tableau)
    latex_code = renderer.render_latex(result.tableau)
    
    print("ASCII Tree:")
    print(ascii_tree)
    
    print("\nTableau Statistics:")
    print(f"Open branches: {result.open_branches}")
    print(f"Closed branches: {result.closed_branches}")
    print(f"Total nodes: {result.total_nodes}")
```

### Rule Application Analysis

```python
from wkrq import solve, parse, T, F

# Demonstrate different rule types
test_cases = [
    ("p & q", T, "T-Conjunction (Alpha rule)"),
    ("p | q", T, "T-Disjunction (Beta rule)"),  
    ("~p", T, "T-Negation (Alpha rule)"),
    ("p -> q", F, "F-Implication (Alpha rule)"),
]

for formula_str, sign, description in test_cases:
    formula = parse(formula_str)
    result = solve(formula, sign)
    
    print(f"\n{description}:")
    print(f"Formula: {sign}:{formula}")
    print(f"Satisfiable: {result.satisfiable}")
    
    if result.tableau:
        renderer = TableauTreeRenderer(show_rules=True)
        tree = renderer.render_ascii(result.tableau)
        print(f"Tree:\n{tree}")
```

## Inference Testing

### Basic Inference Validation

```python
from wkrq import check_inference, parse_inference

# Valid inference: Modus ponens
inference = parse_inference("p, p -> q |- q")
result = check_inference(inference)

print(f"Valid: {result.valid}")
if not result.valid:
    print(f"Countermodels: {result.countermodels}")

# Access underlying tableau
tableau_result = result.tableau_result
print(f"Satisfiable: {tableau_result.satisfiable}")
```

### Complex Inference Patterns

```python
from wkrq import check_inference, parse_inference

# Test various inference patterns
inference_patterns = [
    ("p, p -> q |- q", "Modus ponens"),
    ("p -> q, ~q |- ~p", "Modus tollens"), 
    ("p -> q, q -> r |- p -> r", "Hypothetical syllogism"),
    ("p | q, ~p |- q", "Disjunctive syllogism"),
    ("p |- q", "Invalid: no connection"),
    ("p -> q |- q", "Invalid: affirming consequent"),
]

for inference_str, description in inference_patterns:
    inference = parse_inference(inference_str)
    result = check_inference(inference)
    
    print(f"\n{description}: {inference}")
    print(f"Valid: {result.valid}")
    
    if not result.valid and result.countermodels:
        print(f"Countermodel: {result.countermodels[0]}")
```

## Restricted Quantifiers

### Quantified Formula Construction

```python
from wkrq import Formula, solve, T

# Create quantified formulas programmatically
x = Formula.variable("X")
human_x = Formula.predicate("Human", [x])
mortal_x = Formula.predicate("Mortal", [x])

# Universal quantification: [∀X Human(X)]Mortal(X)
universal = Formula.restricted_forall(x, human_x, mortal_x)
result = solve(universal, T)
print(f"Universal satisfiable: {result.satisfiable}")

# Existential quantification: [∃X Human(X)]Mortal(X)  
existential = Formula.restricted_exists(x, human_x, mortal_x)
result = solve(existential, T)
print(f"Existential satisfiable: {result.satisfiable}")
```

### Quantified Inference

```python
from wkrq import entails, Formula

# Domain-specific reasoning
x = Formula.variable("X")
human_x = Formula.predicate("Human", [x])
mortal_x = Formula.predicate("Mortal", [x])

# Premises
all_humans_mortal = Formula.restricted_forall(x, human_x, mortal_x)
socrates = Formula.constant("socrates")
socrates_human = Formula.predicate("Human", [socrates])

# Conclusion
socrates_mortal = Formula.predicate("Mortal", [socrates])

# Test entailment
premises = [all_humans_mortal, socrates_human]
is_valid = entails(premises, socrates_mortal)
print(f"Socrates inference valid: {is_valid}")
```

## Advanced API Usage

### Custom Formula Construction

```python
from wkrq import Formula, solve, T

# Build complex formulas programmatically
p, q, r = Formula.atoms("p", "q", "r")

# Nested implications: p -> (q -> r)
nested = p.implies(q.implies(r))

# Complex conjunction: (p | q) & (q | r) & (r | p)
complex_conj = (p | q) & (q | r) & (r | p)

# Test satisfiability
result = solve(complex_conj, T)
print(f"Complex formula satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")

# Analyze models
for i, model in enumerate(result.models):
    print(f"Model {i+1}: {model}")
```

### Performance Analysis

```python
import time
from wkrq import solve, Formula, T

# Performance testing
def benchmark_formula(formula_str, iterations=100):
    formula = parse(formula_str)
    
    start_time = time.time()
    for _ in range(iterations):
        result = solve(formula, T)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / iterations
    print(f"Formula: {formula_str}")
    print(f"Average time: {avg_time:.6f}s")
    print(f"Nodes created: {result.total_nodes}")
    return avg_time

# Benchmark different complexity levels
benchmark_formula("p")
benchmark_formula("p & q")  
benchmark_formula("(p | q) & (q | r) & (r | p)")
benchmark_formula("((p -> q) -> ((q -> r) -> (p -> r)))")
```

### Model Extraction and Analysis

```python
from wkrq import solve, parse, T, TRUE, FALSE, UNDEFINED

formula = parse("(p | q) & ~(p & q)")  # Exclusive or
result = solve(formula, T)

if result.satisfiable:
    print(f"Found {len(result.models)} models:")
    
    for i, model in enumerate(result.models):
        print(f"\nModel {i+1}:")
        for atom, value in model.valuations.items():
            value_str = {
                TRUE: "true",
                FALSE: "false", 
                UNDEFINED: "undefined"
            }.get(value, str(value))
            print(f"  {atom} = {value_str}")
```

### Sign System Analysis  

```python
from wkrq import solve, parse, T, F, M, N

formula = parse("p | ~p")  # Classical tautology

# Test all four signs
sign_results = {}
for sign in [T, F, M, N]:
    result = solve(formula, sign)
    sign_results[sign] = result.satisfiable

print("Classical tautology p | ~p:")
print(f"T (must be true): {sign_results[T]}")
print(f"F (must be false): {sign_results[F]}")  
print(f"M (can be true or false): {sign_results[M]}")
print(f"N (must be undefined): {sign_results[N]}")

# This demonstrates weak Kleene semantics:
# - Cannot be false (classical reasoning preserved)
# - Can be undefined (non-classical behavior)
```

### Integration with External Systems

```python
import json
from wkrq import solve, parse, check_inference, parse_inference

def analyze_logical_query(query_data):
    """Process logical queries from external systems."""
    if query_data["type"] == "satisfiability":
        formula = parse(query_data["formula"])
        sign = {"T": T, "F": F, "M": M, "N": N}[query_data["sign"]]
        result = solve(formula, sign)
        
        return {
            "satisfiable": result.satisfiable,
            "models": [str(m) for m in result.models],
            "stats": {
                "nodes": result.total_nodes,
                "open_branches": result.open_branches,
                "closed_branches": result.closed_branches
            }
        }
    
    elif query_data["type"] == "inference":
        inference = parse_inference(query_data["inference"])
        result = check_inference(inference)
        
        return {
            "valid": result.valid,
            "countermodels": [str(m) for m in result.countermodels]
        }

# Example usage
query = {
    "type": "inference",
    "inference": "p -> q, p |- q"
}

result = analyze_logical_query(query)
print(json.dumps(result, indent=2))
```

This API reference demonstrates the comprehensive programmatic interface for wKrQ logical reasoning, suitable for integration into larger applications, research tools, and educational software.
