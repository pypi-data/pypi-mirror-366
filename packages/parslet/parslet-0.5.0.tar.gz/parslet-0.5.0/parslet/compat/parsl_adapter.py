"""Parsl compatibility helpers and AST translators for Parslet.

This module exposes lightweight shims that mimic a subset of the ``parsl``
API so that existing code written for Parsl can run on top of Parslet with
minimal changes.  It also provides AST transformers for converting source code
from Parsl syntax to Parslet syntax.
"""

from __future__ import annotations

import ast
import warnings

from ..core import parslet_task, ParsletFuture


class ParslToParsletTranslator(ast.NodeTransformer):
    """Replace Parsl decorators and APIs with Parslet equivalents."""

    PARSL_DECORATORS = {"python_app", "bash_app"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Replace ``@python_app``/``@bash_app`` with ``@parslet_task``."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id in self.PARSL_DECORATORS
            ):
                decorator.id = "parslet_task"
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Emit a warning when ``DataFlowKernel`` is used."""
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "DataFlowKernel"
        ):
            warnings.warn(
                "Parsl DataFlowKernel is not supported; Parslet manages "
                "scheduling internally.",
                stacklevel=2,
            )
        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "DataFlowKernel"
        ):
            # drop assignment
            return ast.Pass()
        return self.generic_visit(node)


def convert_parsl_to_parslet(code: str) -> str:
    """Convert Parsl-based code string to Parslet syntax."""
    tree = ast.parse(code)
    transformed = ParslToParsletTranslator().visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)


class ParsletToParslTranslator(ast.NodeTransformer):
    """Replace Parslet decorators with Parsl equivalents."""

    PARSLET_DECORATORS = {"parslet_task"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id in self.PARSLET_DECORATORS
            ):
                decorator.id = "python_app"
        return self.generic_visit(node)


def convert_parslet_to_parsl(code: str) -> str:
    """Convert Parslet-based code string to Parsl syntax."""
    tree = ast.parse(code)
    transformed = ParsletToParslTranslator().visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)


# ---------------------------------------------------------------------------
# Runtime compatibility shims
# ---------------------------------------------------------------------------


def python_app(_func=None, **kwargs):
    """Parsl ``python_app`` decorator mapped to :func:`parslet_task`."""

    def wrapper(func):
        return parslet_task(func, **kwargs)

    if _func is None:
        return wrapper
    return wrapper(_func)


def bash_app(_func=None, **kwargs):
    """Parsl ``bash_app`` decorator mapped to :func:`parslet_task`.

    The current implementation executes the decorated Python function as a
    regular Parslet task.  Shell execution semantics of Parsl's ``bash_app``
    are not replicated.
    """

    return python_app(_func, **kwargs)


class DataFlowKernel:  # pragma: no cover - simple shim
    """Minimal stub of Parsl's ``DataFlowKernel``.

    Instantiating this class issues a warning since Parslet manages task
    scheduling internally.
    """

    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "Parsl DataFlowKernel is not supported; Parslet manages "
            "scheduling internally.",
            stacklevel=2,
        )

    def __getattr__(self, attr):
        raise AttributeError(
            "DataFlowKernel is only a compatibility stub in Parslet"
        )


__all__ = [
    "ParslToParsletTranslator",
    "convert_parsl_to_parslet",
    "ParsletToParslTranslator",
    "convert_parslet_to_parsl",
    "python_app",
    "bash_app",
    "DataFlowKernel",
    "ParsletFuture",
]
