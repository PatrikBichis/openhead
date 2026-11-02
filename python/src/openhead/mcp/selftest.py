"""`openhead mcp --selftest`: every tool and resource against a headless simulator."""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from mcp import Client

from ..tokens import TokenStore
from .server import HeadLink, build_server

REPO = Path(__file__).resolve().parents[4]
PNG_1PX = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQ"
                           "GAhKmMIQAAAABJRU5ErkJggg==")


async def selftest() -> int:
    from ..sim import SimServer

    failures = 0

    def report(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  {detail}" if detail else ""), flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        image = Path(tmp) / "pixel.png"
        image.write_bytes(PNG_1PX)
        async with SimServer(host="127.0.0.1", port=0, mdns=False) as sim:
            link = HeadLink(f"127.0.0.1:{sim.port}", client="mcp-selftest",
                            store=TokenStore(Path(tmp) / "tokens.json"))
            try:
                async with Client(build_server(link)) as client:
                    tools = {t.name for t in (await client.list_tools()).tools}
                    report("list_tools", len(tools) >= 13, ", ".join(sorted(tools)))

                    async def tool(name: str, args: dict | None = None, *, expect_error=False):
                        result = await client.call_tool(name, args or {})
                        text = " ".join(getattr(c, "text", f"<{c.type}>") for c in result.content)
                        kinds = [c.type for c in result.content]
                        report(name, result.is_error == expect_error, text[:100].replace("\n", " "))
                        return result, kinds

                    await tool("get_status", expect_error=True)  # not paired yet
                    await tool("pair", {"code": "0000"})
                    await tool("list_themes")
                    await tool("set_theme", {"name": "halloween"})
                    await tool("set_emotion", {"name": "shocked", "intensity": 0.8})
                    await tool("look_at", {"x": 0.5, "y": 0.2})
                    await tool("wait_for", {"topic": "status",
                                            "predicate": {"theme": "halloween"}})
                    await tool("wait_for", {"topic": "log", "predicate": {"contains": "nothing"},
                                            "timeout_s": 0.5}, expect_error=True)
                    _, kinds = await tool("take_screenshot")
                    report("take_screenshot returns an image", kinds == ["image"])
                    await tool("show_image", {"url_or_path": str(image), "overlay": "face-corner"})
                    await tool("show_face")
                    await tool("show_web", {"url": "file:///etc/passwd"}, expect_error=True)
                    await tool("tail_logs", {"n": 10})
                    await tool("get_status")
                    await tool("get_diagnostics")
                    await tool("get_faces", expect_error=True)   # cameras off (idle)
                    await tool("set_mode", {"mode": "capture"})
                    result, _ = await tool("get_faces")          # right after the switch
                    report("get_faces sees people after a mode change",
                           '"bearing"' in " ".join(getattr(c, "text", "") for c in result.content))
                    await tool("set_mode", {"mode": "idle"})
                    smoke =REPO / "scenarios" / "smoke.yaml"
                    if smoke.exists():
                        _, kinds = await tool("run_scenario", {"path": str(smoke)})
                        report("run_scenario returns screenshots", "image" in kinds)
                    for uri in ("openhead://status", "openhead://themes", "openhead://logs"):
                        contents = (await client.read_resource(uri)).contents
                        report(f"resource {uri}", bool(contents and contents[0].text))
            finally:
                await link.close()

    print(f"selftest: {'OK' if not failures else f'{failures} FAILED'}")
    return 1 if failures else 0
