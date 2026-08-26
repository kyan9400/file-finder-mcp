from __future__ import annotations

import heapq
import os
import time
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "target",
        "vendor",
    }
)
MAX_SCANNED_FILES = 200_000


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class SearchModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class FileMatch(SearchModel):
    name: str
    relative_path: str
    absolute_path: str
    extension: str
    size_bytes: int = Field(ge=0)
    modified_at: datetime


class SearchResponse(SearchModel):
    root: str
    query: str
    scanned_files: int = Field(ge=0)
    skipped_entries: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    truncated: bool
    results: list[FileMatch]


def _excluded(relative: str, patterns: tuple[str, ...]) -> bool:
    candidate = PurePosixPath(relative)
    return any(candidate.match(pattern) for pattern in patterns)


def _rank(match: FileMatch, query: str) -> tuple[int, int, int, str]:
    name = match.name.casefold()
    relative = match.relative_path.casefold()
    if name == query:
        category = 0
    elif name.startswith(query):
        category = 1
    elif query in name:
        category = 2
    else:
        category = 3
    return category, relative.count("/"), len(relative), relative


def search_files(
    root: str | Path,
    query: str,
    *,
    max_results: int = 50,
    extensions: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    include_hidden: bool = False,
) -> SearchResponse:
    started = time.perf_counter()
    workspace = Path(root).resolve(strict=True)
    normalized_query = query.strip().casefold()
    if not normalized_query:
        raise ValueError("query must contain a non-whitespace character")
    if not 1 <= max_results <= 500:
        raise ValueError("max_results must be between 1 and 500")

    normalized_extensions = {
        value.casefold() if value.startswith(".") else f".{value.casefold()}"
        for value in extensions
        if value.strip()
    }
    patterns = tuple(value.replace("\\", "/") for value in exclude if value.strip())
    scanned = 0
    skipped = 0

    def candidates():
        nonlocal scanned, skipped
        stack = [workspace]
        while stack and scanned < MAX_SCANNED_FILES:
            directory = stack.pop()
            try:
                entries = sorted(os.scandir(directory), key=lambda entry: entry.name.casefold())
            except OSError:
                skipped += 1
                continue
            child_directories: list[Path] = []
            for entry in entries:
                hidden = entry.name.startswith(".")
                relative = Path(entry.path).relative_to(workspace).as_posix()
                try:
                    if entry.is_dir(follow_symlinks=False):
                        if (
                            entry.name in DEFAULT_EXCLUDED_DIRECTORIES
                            or (hidden and not include_hidden)
                            or _excluded(relative, patterns)
                        ):
                            skipped += 1
                        else:
                            child_directories.append(Path(entry.path))
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        skipped += 1
                        continue
                    scanned += 1
                    if (hidden and not include_hidden) or _excluded(relative, patterns):
                        continue
                    extension = Path(entry.name).suffix.casefold()
                    if normalized_extensions and extension not in normalized_extensions:
                        continue
                    if normalized_query not in relative.casefold():
                        continue
                    stat = entry.stat(follow_symlinks=False)
                    yield FileMatch(
                        name=entry.name,
                        relative_path=relative,
                        absolute_path=str(Path(entry.path).resolve()),
                        extension=extension,
                        size_bytes=stat.st_size,
                        modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                    )
                except OSError:
                    skipped += 1
            stack.extend(reversed(child_directories))

    ranked = heapq.nsmallest(
        max_results + 1,
        candidates(),
        key=lambda match: _rank(match, normalized_query),
    )
    truncated = len(ranked) > max_results or scanned >= MAX_SCANNED_FILES
    return SearchResponse(
        root=str(workspace),
        query=query.strip(),
        scanned_files=scanned,
        skipped_entries=skipped,
        duration_ms=max(0, round((time.perf_counter() - started) * 1000)),
        truncated=truncated,
        results=ranked[:max_results],
    )
