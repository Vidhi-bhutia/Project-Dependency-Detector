import json
from pathlib import Path

from code_impact_analyzer.cli import main


def test_cli_json_output(capsys) -> None:
    root = Path(__file__).parent / "fixtures" / "sample_project"
    exit_code = main(["--root", str(root), "--changed", "auth/login.py", "--json"])
    assert exit_code == 0

    output = capsys.readouterr().out
    data = json.loads(output)
    impacted_paths = {item["path"] for item in data["impacted_modules"]}
    assert impacted_paths == {"api/routes.py", "tests/test_login.py", "user/service.py"}
