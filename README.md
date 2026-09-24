# File Finder MCP

[![CI](https://github.com/kyan9400/file-finder-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/kyan9400/file-finder-mcp/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/kyan9400/file-finder-mcp)](https://github.com/kyan9400/file-finder-mcp/releases)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-0f766e)](LICENSE)

A bounded, ranked file-search server for Model Context Protocol clients. It finds files by partial path without allowing each tool call to choose an arbitrary filesystem root.

## Why it is useful

Large workspaces make broad filesystem searches noisy and expensive. File Finder MCP keeps discovery predictable:

- fixes the search root when the process starts;
- never follows directory symlinks;
- skips version-control, dependency, cache, and build directories;
- caps scanned files and returned matches;
- ranks exact names, prefixes, filenames, and paths deterministically;
- supports extension filters and workspace-relative exclusions;
- returns typed results with scan telemetry;
- includes a standalone CLI for scripts and debugging.

The server targets the stable 2.x MCP Python SDK.

## Install

Requires Python 3.11 or newer.

```bash
python -m pip install .
```

For an isolated command-line installation, `pipx install .` is also suitable.

## Configure an MCP client

Set `FILE_FINDER_ROOT` to the only directory the server should expose:

```json
{
  "mcpServers": {
    "file-finder": {
      "command": "file-finder-mcp",
      "env": {
        "FILE_FINDER_ROOT": "/absolute/path/to/workspace"
      }
    }
  }
}
```

Restart the MCP client after changing its configuration.

A ready-to-edit configuration for Cline is provided in [`examples/cline_config.json`](examples/cline_config.json).

## Tool

`find_files` accepts:

| Argument | Type | Default | Purpose |
| --- | --- | --- | --- |
| `query` | string | required | Case-insensitive filename or path fragment |
| `max_results` | integer | `50` | Result cap from 1 to 500 |
| `extensions` | string array | all | Optional values such as `py`, `.ts`, or `md` |
| `exclude` | string array | none | Workspace-relative glob exclusions |
| `include_hidden` | boolean | `false` | Include hidden paths outside protected defaults |

Example response:

```json
{
  "root": "/workspace",
  "query": "invoice",
  "scannedFiles": 1842,
  "skippedEntries": 14,
  "durationMs": 12.48,
  "truncated": false,
  "results": [
    {
      "path": "/workspace/src/invoice.py",
      "relativePath": "src/invoice.py",
      "name": "invoice.py",
      "extension": ".py",
      "score": 0,
      "sizeBytes": 2740
    }
  ]
}
```

## CLI

The same search engine is available without an MCP client:

```bash
file-finder invoice --root . --extension py --exclude "fixtures/**" --limit 25
```

It writes structured JSON to stdout, which makes it easy to compose with other tools.

## Security model

File Finder MCP returns file metadata, not file contents. The configured root is resolved once at startup. Searches cannot replace it, and directory symlinks are not traversed. Common sensitive or expensive directories such as `.git`, `.env`, `node_modules`, `.venv`, `dist`, and cache folders are excluded by default.

Run one server instance per trust boundary. This is a discovery tool, not an authorization system.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
python -m build
```

CI covers Python 3.11 and 3.13 on Linux and Windows.

## License

[MIT](LICENSE)
