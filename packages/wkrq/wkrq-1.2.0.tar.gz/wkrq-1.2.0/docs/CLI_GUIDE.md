# wKrQ CLI Guide

**Version:** 1.2.0  
**Date:** August 2025  
**Author:** Bradley P. Allen

The wKrQ (weak Kleene logic with restricted Quantification) command-line interface provides comprehensive tools for logical reasoning, tableau construction, and inference validation.

## Installation

```bash
pip install wkrq
```

## Basic Usage

### Formula Satisfiability Testing

Test if a formula can be satisfied under different signs:

```bash
# Test if formula is satisfiable under T (true) sign
wkrq "p & q"

# Test under specific signs
wkrq --sign=T "p | q"    # Must be true
wkrq --sign=F "p & ~p"   # Must be false (unsatisfiable)
wkrq --sign=M "p | ~p"   # Can be true or false
wkrq --sign=N "p"        # Must be undefined
```

### Tableau Tree Visualization

Display the reasoning process with tableau trees:

```bash
# Basic ASCII tree
wkrq --tree "p & q"

# Unicode tree with rule annotations
wkrq --tree --format=unicode --show-rules "p -> q"

# Show all models found
wkrq --models --tree "p | q"
```

### Inference Testing

Test if premises logically entail a conclusion:

```bash
# Using turnstile notation
wkrq "p, p -> q |- q"

# Using --inference flag
wkrq --inference "p, p -> q, q"

# Complex inference with explanation
wkrq --explain --tree --show-rules "p -> (q -> r), p, q |- r"
```

## Signs System

wKrQ uses a four-sign system for tableau construction:

- **T**: Formula must be true
- **F**: Formula must be false  
- **M**: Formula can be true or false (meaningful)
- **N**: Formula must be undefined (non-true)

## Tableau Rules Reference

### Alpha Rules (Non-branching)

These rules extend a single branch:

```bash
# T-Conjunction: T:(A & B) → T:A, T:B
wkrq --sign=T --tree --show-rules "p & q"

# F-Disjunction: F:(A | B) → F:A, F:B  
wkrq --sign=F --tree --show-rules "p | q"

# T-Negation: T:~A → F:A
wkrq --sign=T --tree --show-rules "~p"

# F-Negation: F:~A → T:A
wkrq --sign=F --tree --show-rules "~p"

# F-Implication: F:(A -> B) → T:A, F:B
wkrq --sign=F --tree --show-rules "p -> q"
```

### Beta Rules (Branching)

These rules create multiple branches:

```bash
# T-Disjunction: T:(A | B) → T:A | T:B
wkrq --sign=T --tree --show-rules "p | q"

# F-Conjunction: F:(A & B) → F:A | F:B
wkrq --sign=F --tree --show-rules "p & q"

# T-Implication: T:(A -> B) → F:A | T:B
wkrq --sign=T --tree --show-rules "p -> q"
```

### Epistemic Rules (M/N Signs)

```bash
# M-signs branch to both T and F possibilities
wkrq --sign=M --tree --show-rules "p & q"

# N-signs propagate undefined values
wkrq --sign=N --tree --show-rules "p -> q"
```

## Restricted Quantifiers

wKrQ supports restricted quantification for domain-specific reasoning:

```bash
# Universal quantification: "All humans are mortal"
wkrq --tree --show-rules "[∀X Human(X)]Mortal(X)"

# Existential quantification: "Some human is mortal"  
wkrq --tree --show-rules "[∃X Human(X)]Mortal(X)"

# Quantified inference
wkrq --tree --show-rules "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
```

## Advanced Features

### Output Formats

```bash
# JSON output for programmatic use
wkrq --json "p & q"

# LaTeX for academic papers
wkrq --tree --format=latex "p -> q"

# Statistical analysis
wkrq --stats --tree "complex_formula"
```

### Performance Optimization

```bash
# Show debug information
wkrq --debug --tree "p & q & r"

# Compact display
wkrq --compact --tree "large_formula"
```

### ACrQ Mode (Bilateral Predicates)

```bash
# Enable ACrQ for paraconsistent reasoning
wkrq --mode=acrq "Human(alice) & ¬Human(alice)"

# Bilateral syntax mode
wkrq --mode=acrq --syntax=bilateral "Human*(alice)"
```

## Common Patterns

### Validating Classical Reasoning

```bash
# Modus ponens (valid)
wkrq "p, p -> q |- q"

# Affirming the consequent (invalid)
wkrq "p -> q, q |- p"

# Hypothetical syllogism (valid)
wkrq "p -> q, q -> r |- p -> r"
```

### Testing Logical Properties

```bash
# Classical tautology (not valid in weak Kleene)
wkrq --sign=F "p | ~p"  # Unsatisfiable (cannot be false)
wkrq --sign=N "p | ~p"  # Satisfiable (can be undefined)

# Contradiction
wkrq --sign=T "p & ~p"  # Unsatisfiable (cannot be true)
```

### Complex Formula Analysis

```bash
# Show complete reasoning process
wkrq --tree --show-rules --format=unicode --stats "((p -> q) -> ((q -> r) -> (p -> r)))"

# Find all satisfying models
wkrq --models --tree "(p | q) & (q | r) & (r | p)"
```

## Integration Examples

### Batch Processing

```bash
# Process multiple formulas
echo "p & q" | wkrq --tree
echo "p -> q" | wkrq --inference --explain
```

### Educational Use

```bash
# Step-by-step tableau construction
wkrq --tree --show-rules --format=unicode --explain "complex_inference"

# Visual comparison of different signs
wkrq --sign=T --tree "p | ~p"
wkrq --sign=F --tree "p | ~p" 
wkrq --sign=N --tree "p | ~p"
```

This guide demonstrates the wKrQ CLI's comprehensive features for logical analysis, education, and research applications.
