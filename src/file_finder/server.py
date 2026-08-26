from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from mcp.server import MCPServer
from pydantic import Field

from file_finder.search import SearchResponse, search_files

ROOT = Path(os.getenv("FILE_FINDER_ROOT", os.getcwd())).resolve()
mcp = MCPServer(
    "File Finder",
    instructions=(
        "Search for files inside a fixed workspace boundary. Results are read-only, bounded, "
        "and never follow directory symlinks."
    ),
)


@mcp.tool(title="Find files")
def find_files(
    query: Annotated[
        str,
        Field(min_length=1, max_length=200, description="Case-insensitive path fragment"),
    ],
    max_results: Annotated[
        int,
        Field(ge=1, le=500, description="Maximum number of ranked matches"),
    ] = 50,
    extensions: Annotated[
        list[str] | None,
        Field(description="Optional extensions such as py, ts, or .md"),
    ] = None,
    exclude: Annotated[
        list[str] | None,
        Field(description="Optional workspace-relative glob exclusions"),
    ] = None,
    include_hidden: Annotated[
        bool,
        Field(description="Include hidden files and directories outside protected defaults"),
    ] = False,
) -> SearchResponse:
    """Find and rank matching files inside the configured workspace root."""
    return search_files(
        ROOT,
        query,
        max_results=max_results,
        extensions=tuple(extensions or ()),
        exclude=tuple(exclude or ()),
        include_hidden=include_hidden,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
