from pathlib import Path

from code_impact_analyzer import analyze_change


def test_analyze_change_returns_expected_impacted_modules() -> None:
    root = Path(__file__).parent / "fixtures" / "sample_project"
    report = analyze_change(root, "auth/login.py")

    impacted_paths = {item.path for item in report.impacted_modules}
    assert impacted_paths == {"api/routes.py", "tests/test_login.py", "user/service.py"}


def test_changed_file_not_listed_as_impacted() -> None:
    root = Path(__file__).parent / "fixtures" / "sample_project"
    report = analyze_change(root, "auth/login.py")

    impacted_paths = {item.path for item in report.impacted_modules}
    assert "auth/login.py" not in impacted_paths
