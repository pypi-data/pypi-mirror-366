"""Simple code summarizer."""

import ast
from typing import List


def summarize_python(code: str) -> List[str]:
    """Return function and class names in code."""
    tree = ast.parse(code)
    return [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]

__all__ = ["summarize_python"]
