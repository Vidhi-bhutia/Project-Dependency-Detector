from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_change


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="impact-analyzer",
        description="Predict impacted Python modules for a changed file.",
    )
    parser.add_argument("--root", default=".", help="Project root to analyze (default: current directory)")
    parser.add_argument("--changed", required=True, help="Changed Python file path, relative to root")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print output in JSON format")
    return parser


def _print_human(report: dict[str, object]) -> None:
    changed_file = report["changed_file"]
    impacted = report["impacted_modules"]

    print(f"Editing: {changed_file}")
    print("Impacted modules:")
    if not impacted:
        print("(none)")
        return

    for item in impacted:
        path = item["path"]
        print(f"- {path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = analyze_change(Path(args.root), Path(args.changed)).as_dict()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
