"""The `openhead` CLI end to end: a simulator process and CLI processes talking to it."""

import asyncio
import os
import socket
import sys
from pathlib import Path

from .conftest import REPO, needs_face


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def cli(*args: str, env: dict) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "openhead.cli.main", *args, env=env,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    out, _ = await proc.communicate()
    return proc.returncode, out.decode(errors="replace")


@needs_face
async def test_sim_pair_and_commands(tmp_path: Path):
    port = free_port()
    env = {**os.environ, "OPENHEAD_TOKENS": str(tmp_path / "tokens.json"),
           "OPENHEAD_DEVICE": f"127.0.0.1:{port}"}
    sim = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "openhead.cli.main", "sim", "--headless", "--no-mdns",
        "--host", "127.0.0.1", "--port", str(port), "--tokens", str(tmp_path / "sim.json"),
        env=env, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                _, w = await asyncio.open_connection("127.0.0.1", port)
                w.close()
                break
            except OSError:
                await asyncio.sleep(0.2)

        code, out = await cli("status", env=env)
        assert code == 1 and "not paired" in out
        code, out = await cli("pair", "0000", env=env)
        assert code == 0 and "paired with openhead-sim" in out, out
        code, out = await cli("emotion", "happy", env=env)
        assert code == 0, out
        code, out = await cli("status", env=env)
        assert code == 0 and "happy" in out, out
        shot = tmp_path / "face.png"
        code, out = await cli("screenshot", "-o", str(shot), env=env)
        assert code == 0 and shot.read_bytes().startswith(b"\x89PNG"), out
        code, out = await cli("run", str(REPO / "scenarios" / "smoke.yaml"),
                              "--out", str(tmp_path / "reports"), env=env)
        assert code == 0 and "PASS" in out, out
    finally:
        sim.terminate()
        await sim.wait()
