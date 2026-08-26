from __future__ import annotations

from pathlib import Path

import pytest
from mcp import Client

from file_finder import server


@pytest.mark.anyio
async def test_mcp_tool_returns_structured_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "src" / "invoice_service.py"
    target.parent.mkdir()
    target.write_text("", encoding="utf-8")
    monkeypatch.setattr(server, "ROOT", tmp_path)

    async with Client(server.mcp) as client:
        response = await client.call_tool(
            "find_files",
            {"query": "invoice", "extensions": ["py"], "max_results": 5},
        )

    assert response.is_error is False
    assert response.structured_content is not None
    assert response.structured_content["query"] == "invoice"
    assert response.structured_content["results"][0]["relativePath"] == "src/invoice_service.py"
