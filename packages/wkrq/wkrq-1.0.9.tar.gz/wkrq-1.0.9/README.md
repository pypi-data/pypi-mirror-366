# wKrQ: A Python Implementation of a Semantic Tableau Calculus for Weak Kleene Logic with Restricted Quantification

[![PyPI version](https://badge.fury.io/py/wkrq.svg?v=1.0.9)](https://badge.fury.io/py/wkrq)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bradleypallen/wkrq/actions/workflows/tests.yml/badge.svg)](https://github.com/bradleypallen/wkrq/actions/workflows/tests.yml)

An implementation of a semantic tableau calculus for first-order weak
Kleene logic with restricted quantification, featuring a command-line
interface for satisfiability and inference checking.

## Citation

This implementation is based on the wKrQ tableau system defined in:

**Ferguson, Thomas Macaulay**. "Tableaux and restricted quantification for
systems related to weak Kleene logic." In *International Conference on
Automated Reasoning with Analytic Tableaux and Related Methods*, pp. 3-19.
Cham: Springer International Publishing, 2021.

The tableau construction algorithms and four-sign system (T, F, M, N)
implemented here follow Ferguson's formal definitions. This is a research
implementation created for experimental and educational purposes.

## Research Software Disclaimer

⚠️ **This is research software.** While extensively tested, this
implementation may contain errors or behave unexpectedly in edge cases. It
is intended for research, education, and experimentation. Use in production
systems is not recommended without thorough validation. Please report any
issues or unexpected behavior through the [issue
tracker](https://github.com/bradleypallen/wkrq/issues).

## Features

- 🎯 **Three-valued semantics**: true (t), false (f), undefined (e)
- 🔤 **Weak Kleene logic**: Operations with undefined propagate undefinedness
- 🔢 **Restricted quantification**: Domain-bounded first-order reasoning
- ⚡ **Industrial performance**: Optimized tableau with sub-millisecond response
- 🖥️ **CLI and API**: Both command-line and programmatic interfaces
- 📚 **Comprehensive docs**: Full documentation with examples

## Quick Start

### Installation

```bash
pip install wkrq
```

### Command Line Usage

```bash
# Test a simple formula
wkrq "p & q"

# Test with specific sign (T, F, M, N)
wkrq --sign=N "p | ~p"

# Show all models
wkrq --models "p | q"

# Display tableau tree
wkrq --tree "p -> q"

# First-order logic with restricted quantifiers
wkrq "[∃X Student(X)]Human(X)"
wkrq "[∀X Human(X)]Mortal(X)"

# Inference checking
wkrq --inference "p & q |- p"
wkrq --inference "[∀X Human(X)]Mortal(X), Human(socrates) |- Mortal(socrates)"
```

### Python API

```python
from wkrq import Formula, solve, valid, T, F, M, N

# Create formulas
p, q = Formula.atoms('p', 'q')
formula = p & (q | ~p)

# Test satisfiability
result = solve(formula, T)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")

# Test validity - Ferguson uses classical validity with weak Kleene
# semantics
tautology = p | ~p
print(f"Valid in Ferguson's system: {valid(tautology)}")  # True (classical
                                                         # tautologies are valid)

# Three-valued reasoning
result = solve(p | ~p, N)  # Can it be undefined?
print(f"Can be undefined: {result.satisfiable}")  # True
```

## Syntax and Semantics

### Formal Language Definition

The language of wKrQ is defined by the following BNF grammar:

```bnf
⟨formula⟩ ::= ⟨atom⟩ | ⟨compound⟩ | ⟨quantified⟩

⟨atom⟩ ::= p | q | r | ... | ⟨predicate⟩

⟨predicate⟩ ::= P(⟨term⟩,...,⟨term⟩)

⟨term⟩ ::= ⟨variable⟩ | ⟨constant⟩

⟨variable⟩ ::= X | Y | Z | ...

⟨constant⟩ ::= a | b | c | ...

⟨compound⟩ ::= ¬⟨formula⟩ | (⟨formula⟩ ∧ ⟨formula⟩) | 
               (⟨formula⟩ ∨ ⟨formula⟩) | (⟨formula⟩ → ⟨formula⟩)

⟨quantified⟩ ::= [∃⟨variable⟩ ⟨formula⟩]⟨formula⟩ | 
                 [∀⟨variable⟩ ⟨formula⟩]⟨formula⟩
```

### Truth Tables

wKrQ implements **weak Kleene** three-valued logic with truth values:

- **t** (true)
- **f** (false)  
- **e** (undefined/error)

#### Negation (¬)

| p | ¬p |
|---|-----|
| t | f |
| f | t |
| e | e |

#### Conjunction (∧)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | f | e |
| **f** | f | f | e |
| **e** | e | e | e |

#### Disjunction (∨)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | t | e |
| **f** | t | f | e |
| **e** | e | e | e |

#### Material Implication (→)

| p \ q | t | f | e |
|-------|---|---|---|
| **t** | t | f | e |
| **f** | t | t | e |
| **e** | e | e | e |

### Quantifier Semantics

#### Restricted Existential Quantification: [∃X φ(X)]ψ(X)

The formula is true iff there exists a domain element d such that both
φ(d) and ψ(d) are true. It is false iff for all domain elements d, either
φ(d) is false or ψ(d) is false (but not undefined). It is undefined if any
evaluation results in undefined.

#### Restricted Universal Quantification: [∀X φ(X)]ψ(X)  

The formula is true iff for all domain elements d, either φ(d) is false
or ψ(d) is true. It is false iff there exists a domain element d such that
φ(d) is true and ψ(d) is false. It is undefined if any evaluation results
in undefined.

The key principle of weak Kleene logic is that **any operation involving
an undefined value produces an undefined result**. This differs from strong
Kleene logic where, for example, `t ∨ e = t`.

## Documentation

- 📖 [CLI Guide](docs/wKrQ_CLI_GUIDE.md) - Complete command-line reference
- 🔧 [API Reference](docs/wKrQ_API_REFERENCE.md) - Full Python API documentation
- 🏗️ [Architecture](docs/wKrQ_ARCHITECTURE.md) - System design and theory

## Examples

### Philosophical Logic: Sorites Paradox

```python
from wkrq import Formula, solve, T, N

# Model vague predicates with three-valued logic
heap_1000 = Formula.atom("Heap1000")  # Clearly a heap
heap_999 = Formula.atom("Heap999")    # Borderline case
heap_1 = Formula.atom("Heap1")        # Clearly not a heap

# Sorites principle
sorites = heap_1000.implies(heap_999)

# The paradox dissolves with undefined values
result = solve(heap_999, N)  # Can be undefined
print(f"Borderline case can be undefined: {result.satisfiable}")
```

### First-Order Reasoning

```python
from wkrq import Formula

# Variables and predicates
x = Formula.variable("X")
human = Formula.predicate("Human", [x])
mortal = Formula.predicate("Mortal", [x])

# Restricted quantification
all_humans_mortal = Formula.restricted_forall(x, human, mortal)
print(f"∀-formula: {all_humans_mortal}")  # [∀X Human(X)]Mortal(X)
```

## Development

```bash
# Clone repository
git clone https://github.com/bradleypallen/wkrq.git
cd wkrq

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
ruff check src tests

# Type checking
mypy src
```

## Theory

wKrQ uses a tableau proof system with four signs:

- **T**: Must be true (t)
- **F**: Must be false (f)
- **M**: Can be true or false (t or f)
- **N**: Must be undefined (e)

This enables systematic proof search in three-valued logic while
maintaining classical reasoning as a special case.

**Note**: Our implementation is validated against Ferguson (2021) and uses
classical validity with weak Kleene semantics, meaning classical tautologies
remain valid. See [Ferguson (2021) Analysis - Key
Findings](docs/FERGUSON_2021_ANALYSIS.md) for validation details.

## Performance

Industrial-grade optimizations include:

- O(1) contradiction detection via hash indexing
- Alpha/beta rule prioritization  
- Intelligent branch selection
- Early termination strategies
- Optimized tableau construction

## Citation

If you use wKrQ in academic work, please cite:

```bibtex
@software{wkrq2025,
  title={wKrQ: A Python Implementation of a Semantic Tableau Calculus for
         Weak Kleene Logic with Restricted Quantification},
  author={Allen, Bradley P.},
  year={2025},
  url={https://github.com/bradleypallen/wkrq}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [PyPI Package](https://pypi.org/project/wkrq/)
- [GitHub Repository](https://github.com/bradleypallen/wkrq)
- [Issue Tracker](https://github.com/bradleypallen/wkrq/issues)
- [Documentation](https://github.com/bradleypallen/wkrq/tree/main/docs)
