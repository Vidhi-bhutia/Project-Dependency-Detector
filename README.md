# Code Change Impact Analyzer

A Python package and CLI that predicts which Python modules are impacted when a file changes.

## What it does

Given a changed file (for example `auth/login.py`), the analyzer:

1. Parses project files.
2. Detects function definitions.
3. Builds import and call dependency graphs.
4. Maps function usage across modules.
5. Shows impacted modules.

## Why engineers use it

- Understand blast radius before merging changes.
- Speed up code reviews in large codebases.
- Decide where to add or run tests.

## Installation

```bash
pip install code-change-impact-analyzer
```

For local development:

```bash
pip install -e .[dev]
```

## CLI Usage

```bash
impact-analyzer --root . --changed auth/login.py
```

Options:

- `--root`: project root directory to analyze (default: current directory)
- `--changed`: changed file path relative to root (required)
- `--json`: print JSON output

## Example Output

```text
Editing: auth/login.py
Impacted modules:
- api/routes.py
- user/service.py
- tests/test_login.py
```

## How it works

The tool performs static analysis over Python source files:

- Collects module imports (`import x`, `from x import y`)
- Collects function definitions per module
- Collects function calls per module
- Builds reverse dependency graph to find modules depending on the changed module
- Expands impact by function-level usage signals

## Limitations

- Dynamic imports and metaprogramming are not fully resolved.
- Runtime dispatch and monkey patching are not modeled.
- Best for conventional Python codebases.
