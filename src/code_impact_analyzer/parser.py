from __future__ import annotations

import ast
from pathlib import Path

from .models import ModuleAnalysis


class _ModuleVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: set[str] = set()
        self.function_defs: set[str] = set()
        self.function_calls: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_defs.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_defs.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        function_name = _extract_called_name(node.func)
        if function_name:
            self.function_calls.add(function_name)
        self.generic_visit(node)


def _extract_called_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def module_name_from_path(root: Path, file_path: Path) -> str:
    rel_path = file_path.relative_to(root)
    if rel_path.suffix != ".py":
        raise ValueError(f"Expected a Python file, got: {file_path}")

    parts = list(rel_path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def module_path_from_name(root: Path, module_name: str) -> Path:
    parts = module_name.split(".") if module_name else []
    return root.joinpath(*parts).with_suffix(".py")


def discover_python_files(root: Path) -> list[Path]:
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", "build", "dist", ".mypy_cache", ".pytest_cache"}
    python_files: list[Path] = []

    for path in root.rglob("*.py"):
        if any(part in ignore_dirs for part in path.parts):
            continue
        python_files.append(path)

    return sorted(python_files)


def parse_module_file(file_path: Path) -> ModuleAnalysis:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    visitor = _ModuleVisitor()
    visitor.visit(tree)

    return ModuleAnalysis(
        imports=visitor.imports,
        function_defs=visitor.function_defs,
        function_calls=visitor.function_calls,
    )
