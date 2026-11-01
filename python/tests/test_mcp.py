"""The MCP server: in-process selftest, and over stdio as Claude Code runs it (plan step 5)."""

import asyncio
import os
import sys
from pathlib import Path

import httpx
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

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


async def _wait_http(url: str, headers: dict | None = None) -> None:
    async with httpx.AsyncClient() as http:
        for _ in range(150):
            try:
                await http.get(url, headers=headers)
                return
            except httpx.TransportError:
                await asyncio.sleep(0.1)
    raise TimeoutError(url)


async def test_http_lists_tools_and_needs_the_token(tmp_path: Path):
    """--http with a token: tools/list works with it, 401 without (no head needed for either)."""
    port = free_port()
    env = {**os.environ, "OPENHEAD_TOKENS": str(tmp_path / "tokens.json")}
    server = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "openhead.cli.main", "mcp", "--device", "127.0.0.1:1",
        "--http", f"127.0.0.1:{port}", "--token", "s3cret",
        env=env, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}/mcp"
    try:
        await _wait_http(url)
        async with httpx.AsyncClient() as http:
            assert (await http.post(url, json={})).status_code == 401
        http_client = create_mcp_http_client(headers={"Authorization": "Bearer s3cret"})
        async with Client(streamable_http_client(url, http_client=http_client)) as client:
            names = {t.name for t in (await client.list_tools()).tools}
        assert {"set_emotion", "get_location", "get_environment"} <= names
    finally:
        server.terminate()
        await server.wait()


async def test_http_on_the_network_refuses_without_token():
    code, out = await cli("mcp", "--http", f"0.0.0.0:{free_port()}", env={**os.environ, "OPENHEAD_MCP_TOKEN": ""})
    assert code != 0 and "needs --token" in out
