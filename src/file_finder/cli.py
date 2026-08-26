from __future__ import annotations

import argparse
import json
from pathlib import Path

from file_finder.search import search_files


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Find files inside a bounded workspace")
    command.add_argument("query", help="case-insensitive path fragment")
    command.add_argument("--root", default=".", help="workspace root")
    command.add_argument("--limit", type=int, default=50, help="maximum results (1-500)")
    command.add_argument("--extension", action="append", default=[], help="extension filter")
    command.add_argument("--exclude", action="append", default=[], help="exclusion glob")
    command.add_argument("--include-hidden", action="store_true", help="include hidden entries")
    return command


def main(arguments: list[str] | None = None) -> int:
    command = parser()
    options = command.parse_args(arguments)
    try:
        result = search_files(
            Path(options.root),
            options.query,
            max_results=options.limit,
            extensions=tuple(options.extension),
            exclude=tuple(options.exclude),
            include_hidden=options.include_hidden,
        )
    except (OSError, ValueError) as error:
        command.error(str(error))
    print(json.dumps(result.model_dump(mode="json", by_alias=True), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
