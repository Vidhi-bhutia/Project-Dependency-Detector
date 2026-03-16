from __future__ import annotations

from collections import deque
from pathlib import Path

from .models import ImpactReport, ImpactedModule, ModuleAnalysis
from .parser import discover_python_files, module_name_from_path, module_path_from_name, parse_module_file


def _resolve_imported_modules(import_name: str, known_modules: set[str]) -> set[str]:
    resolved: set[str] = set()

    if import_name in known_modules:
        resolved.add(import_name)

    prefix = import_name
    while "." in prefix:
        prefix = prefix.rsplit(".", 1)[0]
        if prefix in known_modules:
            resolved.add(prefix)

    for module in known_modules:
        if module.startswith(import_name + "."):
            resolved.add(module)

    return resolved


def _build_reverse_dependency_graph(module_map: dict[str, ModuleAnalysis]) -> dict[str, set[str]]:
    known_modules = set(module_map)
    reverse_graph: dict[str, set[str]] = {module: set() for module in module_map}

    for module, analysis in module_map.items():
        for imported in analysis.imports:
            for resolved in _resolve_imported_modules(imported, known_modules):
                reverse_graph.setdefault(resolved, set()).add(module)

    return reverse_graph


def _transitive_dependents(changed_module: str, reverse_graph: dict[str, set[str]]) -> set[str]:
    impacted: set[str] = set()
    queue: deque[str] = deque([changed_module])
    visited: set[str] = {changed_module}

    while queue:
        current = queue.popleft()
        for dependent in reverse_graph.get(current, set()):
            if dependent in visited:
                continue
            visited.add(dependent)
            impacted.add(dependent)
            queue.append(dependent)

    return impacted


def analyze_change(root: str | Path, changed_file: str | Path) -> ImpactReport:
    root_path = Path(root).resolve()
    changed_path = (root_path / changed_file).resolve() if not Path(changed_file).is_absolute() else Path(changed_file).resolve()

    if not changed_path.exists() or changed_path.suffix != ".py":
        raise FileNotFoundError(f"Changed file does not exist or is not a .py file: {changed_file}")

    python_files = discover_python_files(root_path)
    module_to_path: dict[str, Path] = {}
    module_map: dict[str, ModuleAnalysis] = {}

    for file_path in python_files:
        module_name = module_name_from_path(root_path, file_path)
        module_to_path[module_name] = file_path
        module_map[module_name] = parse_module_file(file_path)

    changed_module = module_name_from_path(root_path, changed_path)
    if changed_module not in module_map:
        raise ValueError(f"Changed module was not discovered during analysis: {changed_module}")

    reverse_graph = _build_reverse_dependency_graph(module_map)
    impacted_by_import = _transitive_dependents(changed_module, reverse_graph)

    changed_functions = module_map[changed_module].function_defs
    impacted_entries: list[ImpactedModule] = []

    for module in sorted(impacted_by_import):
        reasons: list[str] = ["imports-or-transitively-depends-on-changed-module"]
        if changed_functions and module_map[module].function_calls.intersection(changed_functions):
            reasons.append("calls-function-defined-in-changed-module")

        resolved_path = module_to_path.get(module) or module_path_from_name(root_path, module)
        relative_path = str(resolved_path.relative_to(root_path)).replace("\\", "/")
        impacted_entries.append(
            ImpactedModule(module=module, path=relative_path, reasons=tuple(reasons))
        )

    changed_relative = str(changed_path.relative_to(root_path)).replace("\\", "/")
    return ImpactReport(
        changed_file=changed_relative,
        changed_module=changed_module,
        impacted_modules=tuple(impacted_entries),
    )
