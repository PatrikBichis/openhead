"""Protocol 0.5: the camera topic, LiDAR on a simulated Pro model, and `openhead cockpit`."""

import asyncio
import base64
import json
import urllib.request

import pytest
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from openhead.client import Head, HeadError
from openhead.cockpit import Cockpit
from openhead.sim import SimServer

from .conftest import FACE_BUILT, needs_face


async def first(sub, timeout=8):
    async def get():
        async for msg in sub:
            return msg
    return await asyncio.wait_for(get(), timeout)


async def watching(sim) -> bool:
    return await sim.face._call("() => !document.querySelector('#watching').hidden")


async def test_camera_frames_and_the_marker(head, sim):
    await head.mode.set("capture")
    async with head.subscribe("camera", 10, max_px=200) as sub:
        frame = await first(sub)
        assert base64.b64decode(frame.jpeg)[:2] == b"\xff\xd8"  # a JPEG
        assert (frame.width, frame.source) == (200, "sim") and frame.height < 200
        assert sim.camera_viewers() == 1
        assert (await head.system.status()).camera_viewers == 1
        await asyncio.sleep(0.1)
        assert await watching(sim)
    await asyncio.sleep(0.2)
    assert sim.camera_viewers() == 0 and not await watching(sim)


async def test_no_frames_in_idle(head):
    async with head.subscribe("camera", 10) as sub:
        with pytest.raises(TimeoutError):
            await first(sub, timeout=0.6)


async def test_lidar_is_optional(head):
    assert "lidar" not in head.welcome.capabilities and "camera.stream" in head.welcome.capabilities
    await head.mode.set("sensing")
    with pytest.raises(HeadError) as exc:
        await head.depth.sample([(0.5, 0.5)])
    assert exc.value.code == "unsupported"
    with pytest.raises(HeadError):
        await head.command("subscribe", topic="mesh", rate_hz=1)


@pytest.fixture
async def pro(store):
    if not FACE_BUILT:
        pytest.skip("face/dist missing")
    server = SimServer(host="127.0.0.1", port=0, mdns=False, validate_outgoing=True, pro=True)
    await server.start()
    h = await Head.connect("127.0.0.1", server.port, client="pytest-pro", store=store)
    await h.pair("0000")
    yield h
    await h.close()
    await server.stop()
    assert server.violations == []


async def test_pro_depth_and_mesh(pro):
    assert {"lidar", "scene_mesh"} <= set(pro.welcome.capabilities)
    with pytest.raises(HeadError):  # needs sensing
        await pro.depth.sample([(0.5, 0.5)])
    await pro.mode.set("sensing")
    depths = await pro.depth.sample([(0.5, 0.2), (0.5, 0.95)])
    assert all(isinstance(d, float) and 0 < d < 6 for d in depths)
    async with pro.subscribe("mesh", 1) as sub:
        msg = await first(sub)
        assert {a.id for a in msg.anchors} == {"floor", "wall-front", "wall-left"}
        assert len(base64.b64decode(msg.anchors[0].vertices)) == 4 * 3 * 4


# --- the cockpit's server ---------------------------------------------------------------


@pytest.fixture
async def cockpit(head):
    c = Cockpit(head, port=0)
    await c.start()
    yield c
    await c.stop()


def get(url: str, host: str | None = None) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, headers={"Host": host} if host else {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, b"", {}


async def test_cockpit_serves_its_page_only(cockpit):
    base = f"http://127.0.0.1:{cockpit.port}"
    status, body, headers = await asyncio.to_thread(get, base + "/")
    assert status == 200 and b"OpenHead cockpit" in body
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert (await asyncio.to_thread(get, base + "/cockpit.js"))[0] == 200
    assert (await asyncio.to_thread(get, base + "/../server.py"))[0] == 404
    # DNS rebinding: a page on another name that resolves here is refused.
    assert (await asyncio.to_thread(get, base + "/", "evil.example:80"))[0] == 403


async def test_cockpit_bridge_needs_its_key_and_origin(cockpit):
    url = f"ws://127.0.0.1:{cockpit.port}/ws"
    origin = f"http://127.0.0.1:{cockpit.port}"
    for bad_url, bad_origin in ((f"{url}?k=nope", origin), (f"{url}?k={cockpit.key}", "http://evil.example")):
        with pytest.raises(InvalidStatus):
            async with connect(bad_url, origin=bad_origin):
                pass
    async with connect(f"{url}?k={cockpit.key}", origin=origin) as ws:
        hello = json.loads(await ws.recv())
        assert hello["op"] == "hello" and hello["connected"] and "camera.stream" in hello["capabilities"]


async def test_cockpit_bridge_commands_say_and_topics(cockpit, sim):
    origin = f"http://127.0.0.1:{cockpit.port}"
    async with connect(f"ws://127.0.0.1:{cockpit.port}/ws?k={cockpit.key}", origin=origin) as ws:
        await ws.recv()  # hello

        async def reply(op: str) -> dict:
            while True:
                msg = json.loads(await asyncio.wait_for(ws.recv(), 8))
                if msg["op"] == op:
                    return msg

        await ws.send(json.dumps({"op": "command", "id": "1", "type": "face.set_emotion",
                                  "params": {"name": "curious", "intensity": 0.8}}))
        assert (await reply("result"))["ok"]
        assert (await sim.face.state())["emotion"] == "curious"
        await ws.send(json.dumps({"op": "command", "id": "2", "type": "depth.sample",
                                  "params": {"points": [{"x": 0.5, "y": 0.5}]}}))
        assert (await reply("result"))["error"]["code"] == "unsupported"  # no LiDAR
        await ws.send(json.dumps({"op": "say", "id": "3", "text": "[happy] Hi! [laugh]"}))
        assert (await reply("result"))["result"]["utterance_id"].startswith("u-")
        await ws.send(json.dumps({"op": "command", "id": "4", "type": "mode.set", "params": {"mode": "capture"}}))
        await reply("result")
        await ws.send(json.dumps({"op": "subscribe", "topic": "camera", "rate_hz": 10, "max_px": 160}))
        frame = await reply("topic")
        assert frame["topic"] == "camera" and frame["data"]["width"] == 160
        await ws.send(json.dumps({"op": "subscribe", "topic": "mesh", "rate_hz": 1}))
        assert (await reply("topic_error"))["code"] == "unsupported"
    await asyncio.sleep(0.3)
    assert sim.camera_viewers() == 0  # the page went away, so did its subscriptions


# --- the page, in Chromium --------------------------------------------------------------


@needs_face
async def test_cockpit_page_cards_layout_and_joke(cockpit, sim):
    from playwright.async_api import async_playwright, expect

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(cockpit.url)
        cards = page.locator(".card")
        await expect(cards).to_have_count(8)
        await expect(page.locator("#device")).to_have_attribute("data-state", "on")
        # Camera: switch to capture in the Mode card, a frame shows.
        await page.locator('.card[data-id="mode"] button', has_text="Capture").click()
        await expect(page.locator(".video img")).to_be_visible(timeout=8000)
        # The joke from the film is a preset; the head says it and smiles at the cue.
        say = page.locator('.card[data-id="say"]')
        await say.locator(".chip", has_text="Meeting").click()
        await say.locator(".chip", has_text="Joke").click()
        await expect(say.locator("textarea")).to_have_value(
            "[happy] Why did the robot go on holiday? [pause] It needed to recharge! [laugh]")
        await say.get_by_role("button", name="Say").click()
        await expect(say.locator(".feed li").first).to_be_visible(timeout=5000)
        for _ in range(40):
            if (await sim.face.state())["emotion"] in ("happy", "laughing"):
                break
            await asyncio.sleep(0.1)
        assert (await sim.face.state())["emotion"] in ("happy", "laughing")
        # Layout: remove a card, add one, reload: it stays as the user left it.
        await page.locator('.card[data-id="imu"] .close').click()
        await page.locator("#add-card").click()
        await page.get_by_role("menuitem", name="LiDAR depth (Pro)").click()
        await page.reload()
        ids = await cards.evaluate_all("cs => cs.map(c => c.dataset.id)")
        assert "imu" not in ids and ids[-1] == "lidar"
        await expect(page.locator('.card[data-id="lidar"]')).to_contain_text("no LiDAR")
        await expect(page.locator('.card[data-id="lidar"]')).to_have_class("card disabled-card")
        await page.get_by_role("button", name="Reset layout").click()
        await expect(cards).to_have_count(8)
        assert errors == []
        await browser.close()
