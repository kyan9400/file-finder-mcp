# File Finder MCP

A small Model Context Protocol server that searches for files below its current working directory.

It exposes one tool, `find_files`. The tool accepts a path fragment, performs a case-insensitive recursive search, and returns matching file names, absolute paths, sizes, and timestamps as JSON.

## Requirements

- Python 3.10 or newer
- The Python `mcp` package
- An MCP-compatible client such as Cline

## Setup

```bash
git clone https://github.com/kyan9400/file-finder-mcp.git
cd file-finder-mcp

python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependency:

```bash
python -m pip install mcp
```

## Client configuration

The repository includes a small Cline configuration example. Use an absolute path to the server script in your own configuration:

```json
{
  "mcpServers": {
    "file-finder-mcp": {
      "command": "python",
      "args": [
        "C:\\path\\to\\file-finder-mcp\\file_finder_server.py"
      ],
      "autoApprove": [],
      "disabled": false
    }
  }
}
```

Restart the client after changing its MCP configuration.

## Tool

### `find_files`

Input:

```json
{
  "path_fragment": "test"
}
```

Example response:

```json
[
  {
    "file_name": "test_config.py",
    "path": "C:\\projects\\example\\test_config.py",
    "size": 1240,
    "created": "2026-01-15T10:30:00"
  }
]
```

The search begins in the server process's current working directory. The fragment is matched against the full path, not only the file name.

## Running it directly

```bash
python file_finder_server.py
```

The server communicates over standard input and output, so it normally runs under an MCP client rather than as a standalone interactive program.

## Current limitations

- Each request walks the directory tree again.
- There are no exclusion patterns or result limits yet.
- The returned `created` value comes from `st_ctime`; its exact meaning differs between operating systems.
