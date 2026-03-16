from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModuleAnalysis:
    imports: set[str]
    function_defs: set[str]
    function_calls: set[str]


@dataclass(frozen=True)
class ImpactedModule:
    module: str
    path: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ImpactReport:
    changed_file: str
    changed_module: str
    impacted_modules: tuple[ImpactedModule, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "changed_file": self.changed_file,
            "changed_module": self.changed_module,
            "impacted_modules": [
                {"module": item.module, "path": item.path, "reasons": list(item.reasons)}
                for item in self.impacted_modules
            ],
        }
