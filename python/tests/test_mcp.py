"""The MCP server: in-process selftest, and over stdio as Claude Code runs it (plan step 5)."""

import asyncio
import os
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters

from openhead.mcp.selftest import selftest

from .conftest import needs_face
from .test_cli import cli, free_port


@needs_face
async def test_selftest():
    assert await selftest() == 0


@needs_face
async def test_stdio_set_theme_screenshot_and_logs(tmp_path: Path):
    port = free_port()
    env = {**os.environ, "OPENHEAD_TOKENS": str(tmp_path / "tokens.json"),
           "OPENHEAD_DEVICE": f"127.0.0.1:{port}"}
    sim = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "openhead.cli.main", "sim", "--headless", "--no-mdns",
        "--host", "127.0.0.1", "--port", str(port), "--tokens", str(tmp_path / "sim.json"),
        env=env, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    try:
        for _ in range(100):
            code, _ = await cli("pair", "0000", env=env)
            if code == 0:
                break
            await asyncio.sleep(0.2)
        params = StdioServerParameters(command=sys.executable,
                                       args=["-m", "openhead.cli.main", "mcp"], env=env)
        async with Client(params) as client:
            result = await client.call_tool("set_theme", {"name": "minimal"})
            assert not result.is_error, result.content
            result = await client.call_tool("take_screenshot", {"scale": 0.25})
            assert not result.is_error and result.content[0].type == "image"
            result = await client.call_tool("tail_logs", {"n": 20})
            assert not result.is_error and "theme=minimal" in result.content[0].text
    finally:
        sim.terminate()
        await sim.wait()
