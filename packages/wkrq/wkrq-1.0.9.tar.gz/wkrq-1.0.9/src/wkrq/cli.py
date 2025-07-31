"""
wKrQ command-line interface.

Comprehensive CLI for wKrQ logic with tableau visualization and inference testing.
"""

import argparse
import json
import sys
from dataclasses import asdict

from . import __version__
from .api import InferenceResult, check_inference
from .parser import ParseError, parse, parse_inference
from .signs import T, sign_from_string
from .tableau import Tableau, TableauNode, TableauResult, solve


class TableauTreeRenderer:
    """Render tableau trees in various formats."""

    def __init__(
        self,
        show_rules: bool = False,
        show_steps: bool = False,
        highlight_closures: bool = False,
        compact: bool = False,
    ):
        self.show_rules = show_rules
        self.show_steps = show_steps
        self.highlight_closures = highlight_closures
        self.compact = compact

    def render_ascii(self, tableau: Tableau) -> str:
        """Render tableau as ASCII art tree."""
        if not tableau.nodes:
            return "Empty tableau"

        lines: list[str] = []
        self._render_node_ascii(tableau.nodes[0], lines, "", True)
        return "\n".join(lines)

    def _render_node_ascii(
        self, node: TableauNode, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Recursively render node and children."""
        # Node representation
        node_str = f"{node.id}. {node.formula}"
        if self.show_rules and node.rule_applied:
            node_str += f" ({node.rule_applied})"

        # Add prefix
        if prefix:
            connector = "└─ " if is_last else "├─ "
            lines.append(prefix + connector + node_str)
        else:
            lines.append(node_str)

        # Handle children
        if node.children:
            # Determine new prefix
            extension = "   " if is_last else "│  "
            new_prefix = prefix + extension

            for i, child in enumerate(node.children):
                is_child_last = i == len(node.children) - 1
                self._render_node_ascii(child, lines, new_prefix, is_child_last)
        elif node.is_closed:
            # Show closure
            closure_symbol = "✗ CLOSED"
            if node.closure_reason:
                closure_symbol += f" ({node.closure_reason})"

            extension = "   " if is_last else "│  "
            lines.append(prefix + extension + "│")
            lines.append(prefix + extension + "└─ " + closure_symbol)

    def render_unicode(self, tableau: Tableau) -> str:
        """Render tableau with Unicode box drawing."""
        if not tableau.nodes:
            return "Empty tableau"

        lines: list[str] = []
        self._render_node_unicode(tableau.nodes[0], lines, "", True)
        return "\n".join(lines)

    def _render_node_unicode(
        self, node: TableauNode, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Recursively render node with Unicode characters."""
        # Node representation
        node_str = f"{node.id}. {node.formula}"
        if self.show_rules and node.rule_applied:
            node_str += f" ({node.rule_applied})"

        # Add prefix with Unicode
        if prefix:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + node_str)
        else:
            lines.append("┌─ " + node_str + " ─┐")

        # Handle children
        if node.children:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension

            for i, child in enumerate(node.children):
                is_child_last = i == len(node.children) - 1
                self._render_node_unicode(child, lines, new_prefix, is_child_last)
        elif node.is_closed:
            closure_symbol = "✗ CLOSED"
            if node.closure_reason:
                closure_symbol += f" ({node.closure_reason})"

            extension = "    " if is_last else "│   "
            lines.append(prefix + extension + "│")
            lines.append(prefix + extension + "└── " + closure_symbol)

    def render_latex(self, tableau: Tableau) -> str:
        """Generate LaTeX/TikZ code for tableau tree."""
        lines = [
            "\\begin{tikzpicture}[",
            "  node distance=1.5cm,",
            "  every node/.style={draw, rectangle, minimum width=2cm, text width=3cm, align=center}",
            "]",
        ]

        # Generate nodes
        node_positions = {}
        for i, node in enumerate(tableau.nodes):
            node_id = f"n{node.id}"
            node_positions[node.id] = node_id

            formula_str = str(node.formula).replace("&", "\\land").replace("|", "\\lor")
            formula_str = formula_str.replace("->", "\\rightarrow").replace(
                "~", "\\neg"
            )

            if i == 0:
                lines.append(f"  \\node ({node_id}) {{{node.id}. {formula_str}}};")
            else:
                # Position relative to parent
                if node.parent:
                    parent_id = f"n{node.parent.id}"
                    lines.append(
                        f"  \\node ({node_id}) [below of={parent_id}] {{{node.id}. {formula_str}}};"
                    )

        # Generate edges
        for node in tableau.nodes:
            if node.parent:
                parent_id = f"n{node.parent.id}"
                node_id = f"n{node.id}"
                rule_label = node.rule_applied or ""
                lines.append(
                    f"  \\draw[->] ({parent_id}) -- node[right] {{{rule_label}}} ({node_id});"
                )

        lines.append("\\end{tikzpicture}")
        return "\n".join(lines)

    def render_json(self, tableau: Tableau) -> dict:
        """Generate JSON representation of tableau tree."""
        nodes = []
        for node in tableau.nodes:
            node_data = {
                "id": node.id,
                "formula": str(node.formula),
                "rule": node.rule_applied,
                "closed": node.is_closed,
                "closure_reason": node.closure_reason,
                "children": [child.id for child in node.children],
            }
            if node.parent:
                node_data["parent"] = node.parent.id
            nodes.append(node_data)

        return {
            "nodes": nodes,
            "open_branches": len(tableau.open_branches),
            "closed_branches": len(tableau.closed_branches),
            "total_nodes": len(tableau.nodes),
        }


def display_result(
    result: TableauResult,
    show_models: bool = True,
    show_stats: bool = False,
    debug: bool = False,
) -> None:
    """Display tableau result."""
    print(f"Satisfiable: {result.satisfiable}")

    if show_models and result.models:
        print(f"Models ({len(result.models)}):")
        for i, model in enumerate(result.models, 1):
            print(f"  {i}. {model}")

    if show_stats:
        print("\nStatistics:")
        print(f"  Open branches: {result.open_branches}")
        print(f"  Closed branches: {result.closed_branches}")
        print(f"  Total nodes: {result.total_nodes}")

    if debug and result.tableau:
        print("\nDebug info:")
        print(f"  Branch details: {len(result.tableau.branches)} total branches")
        for i, branch in enumerate(result.tableau.branches):
            status = "CLOSED" if branch.is_closed else "OPEN"
            print(f"    Branch {i}: {status} ({len(branch.nodes)} nodes)")


def display_inference_result(result: InferenceResult, explain: bool = False) -> None:
    """Display inference test result."""
    if result.valid:
        print("✓ Valid inference")
    else:
        print("✗ Invalid inference")
        if result.countermodels:
            print("Countermodels:")
            for i, model in enumerate(result.countermodels, 1):
                print(f"  {i}. {model}")

    if explain:
        print("\nExplanation:")
        print(f"Testing satisfiability of: {result.inference.to_formula()}")
        display_result(result.tableau_result, show_models=False, show_stats=True)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="wKrQ - Weak Kleene logic with restricted quantification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wkrq "p & ~p"                    # Test satisfiability
  wkrq --sign=M "p | ~p"           # Test with M sign
  wkrq "p, p -> q |- q"            # Test inference validity
  wkrq --tree "p & (q | r)"        # Show tableau tree
  wkrq --models "p | q"            # Show all models
  wkrq --tree --format=unicode "p -> q"  # Unicode tree display
        """,
    )

    parser.add_argument("input", nargs="?", help="Formula or inference to evaluate")
    parser.add_argument("--version", action="version", version=f"wKrQ {__version__}")
    parser.add_argument(
        "--sign",
        default="T",
        choices=["T", "F", "M", "N"],
        help="Sign to test (default: T)",
    )
    parser.add_argument("--models", action="store_true", help="Show all models")
    parser.add_argument("--stats", action="store_true", help="Show tableau statistics")
    parser.add_argument("--debug", action="store_true", help="Show debug information")

    # Inference testing
    parser.add_argument(
        "--consequence",
        choices=["strong", "weak"],
        default="strong",
        help="Type of consequence relation",
    )
    parser.add_argument(
        "--explain", action="store_true", help="Explain inference result"
    )
    parser.add_argument(
        "--countermodel",
        action="store_true",
        help="Show countermodel for invalid inference",
    )

    # Tree visualization
    parser.add_argument("--tree", action="store_true", help="Display tableau tree")
    parser.add_argument(
        "--format",
        choices=["ascii", "unicode", "latex", "json"],
        default="ascii",
        help="Tree display format",
    )
    parser.add_argument(
        "--show-rules", action="store_true", help="Show rule names in tree"
    )
    parser.add_argument(
        "--show-steps", action="store_true", help="Show step numbers in tree"
    )
    parser.add_argument(
        "--highlight-closures", action="store_true", help="Highlight closed branches"
    )
    parser.add_argument("--compact", action="store_true", help="Compact tree display")
    parser.add_argument(
        "--interactive", action="store_true", help="Step-by-step tableau construction"
    )

    # Output formats
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    # Interactive mode if no input
    if not args.input:
        interactive_mode()
        return

    try:
        # Parse input
        if "|-" in args.input:
            # Inference
            inference = parse_inference(args.input)
            inference_result = check_inference(inference)

            if args.json:
                output = {
                    "type": "inference",
                    "inference": str(inference),
                    "valid": inference_result.valid,
                    "countermodels": [
                        asdict(m) for m in inference_result.countermodels
                    ],
                }
                print(json.dumps(output, indent=2))
            else:
                display_inference_result(inference_result, args.explain or args.debug)

                if args.tree and inference_result.tableau_result.tableau:
                    print("\nTableau tree:")
                    renderer = TableauTreeRenderer(
                        args.show_rules,
                        args.show_steps,
                        args.highlight_closures,
                        args.compact,
                    )
                    tree_str = render_tree(
                        inference_result.tableau_result.tableau, args.format, renderer
                    )
                    print(tree_str)

        else:
            # Formula
            formula = parse(args.input)
            sign = sign_from_string(args.sign)
            tableau_result = solve(formula, sign)

            if args.json:
                output = {
                    "type": "formula",
                    "formula": str(formula),
                    "sign": str(sign),
                    "satisfiable": tableau_result.satisfiable,
                    "models": [asdict(m) for m in tableau_result.models],
                    "stats": {
                        "open_branches": tableau_result.open_branches,
                        "closed_branches": tableau_result.closed_branches,
                        "total_nodes": tableau_result.total_nodes,
                    },
                }
                print(json.dumps(output, indent=2))
            else:
                display_result(tableau_result, args.models, args.stats, args.debug)

                if args.tree and tableau_result.tableau:
                    print("\nTableau tree:")
                    renderer = TableauTreeRenderer(
                        args.show_rules,
                        args.show_steps,
                        args.highlight_closures,
                        args.compact,
                    )
                    tree_str = render_tree(
                        tableau_result.tableau, args.format, renderer
                    )
                    print(tree_str)

    except ParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if args.debug:
            raise
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def render_tree(
    tableau: Tableau, format_type: str, renderer: TableauTreeRenderer
) -> str:
    """Render tableau tree in specified format."""
    if format_type == "ascii":
        return renderer.render_ascii(tableau)
    elif format_type == "unicode":
        return renderer.render_unicode(tableau)
    elif format_type == "latex":
        return renderer.render_latex(tableau)
    elif format_type == "json":
        json_data = renderer.render_json(tableau)
        return json.dumps(json_data, indent=2)
    else:
        raise ValueError(f"Unknown format: {format_type}")


def interactive_mode() -> None:
    """Interactive REPL mode."""
    print("wKrQ Interactive Mode")
    print("Commands: formula, inference (P |- Q), help, quit")
    print()

    while True:
        try:
            line = input("wkrq> ").strip()

            if not line:
                continue

            if line.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if line.lower() in ["help", "h"]:
                print("Commands:")
                print("  formula           - Enter a formula to test")
                print("  P, Q |- R         - Test inference")
                print("  help              - Show this help")
                print("  quit              - Exit")
                continue

            # Parse and evaluate
            if "|-" in line:
                inference = parse_inference(line)
                result = check_inference(inference)
                display_inference_result(result)
            else:
                formula = parse(line)
                tableau_result = solve(formula, T)
                display_result(tableau_result)

        except ParseError as e:
            print(f"Parse error: {e}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
