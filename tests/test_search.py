from __future__ import annotations

import json
from pathlib import Path

import pytest

from file_finder.cli import main
from file_finder.search import search_files


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    files = {
        "src/report.py": "print('report')",
        "src/report_builder.py": "",
        "src/nested/monthly_report.py": "",
        "src/report.ts": "",
        "docs/report.md": "",
        ".private/report.txt": "",
        "node_modules/report.js": "",
    }
    for name, content in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return tmp_path


def test_ranks_exact_names_before_deeper_matches(workspace: Path) -> None:
    result = search_files(workspace, "report.py")

    assert [match.relative_path for match in result.results] == [
        "src/report.py",
        "src/nested/monthly_report.py",
    ]
    assert result.scanned_files == 5
    assert result.skipped_entries == 2


def test_filters_extensions_and_globs(workspace: Path) -> None:
    result = search_files(
        workspace,
        "report",
        extensions=(".py",),
        exclude=("src/nested/**",),
    )

    assert [match.relative_path for match in result.results] == [
        "src/report.py",
        "src/report_builder.py",
    ]


def test_hidden_files_require_explicit_opt_in(workspace: Path) -> None:
    default = search_files(workspace, "private")
    visible = search_files(workspace, "private", include_hidden=True)

    assert default.results == []
    assert visible.results[0].relative_path == ".private/report.txt"


def test_limit_marks_response_as_truncated(workspace: Path) -> None:
    result = search_files(workspace, "report", max_results=2)

    assert len(result.results) == 2
    assert result.truncated is True


def test_cli_returns_structured_json(workspace: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["report", "--root", str(workspace), "--limit", "1"]) == 0

    result = json.loads(capsys.readouterr().out)
    assert result["query"] == "report"
    assert len(result["results"]) == 1
    assert result["results"][0]["relativePath"] == "src/report.py"


@pytest.mark.parametrize("query", ["", "   "])
def test_blank_queries_are_rejected(workspace: Path, query: str) -> None:
    with pytest.raises(ValueError, match="query"):
        search_files(workspace, query)
