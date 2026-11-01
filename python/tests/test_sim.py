"""Protocol behaviour of the simulator, exercised through the client library."""

import asyncio
import base64
import json
import math
import urllib.error
import urllib.request

import pytest
from websockets.asyncio.client import connect

from openhead.client import Head, HeadError
from openhead.protocol import models
from openhead.sim import SimServer

PNG_1PX = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
           "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


async def raw(sim: SimServer, *messages: dict) -> list[dict]:
    """Send raw messages on a fresh connection and return one reply per message."""
    replies = []
    async with connect(f"ws://127.0.0.1:{sim.port}") as ws:
        for i, m in enumerate(messages):
            await ws.send(json.dumps({"ts": 1, "seq": i, **m}))
            replies.append(json.loads(await ws.recv()))
    return replies


# --- handshake and pairing ---------------------------------------------------


async def test_commands_need_pairing(sim):
    [reply] = await raw(sim, {"type": "face.blink", "id": "a"})
    assert reply["type"] == "error" and reply["code"] == "unauthorized" and reply["id"] == "a"


async def test_hello_without_token_requires_pairing(sim, store):
    head = await Head.connect("127.0.0.1", sim.port, client="t", store=store)
    assert not head.paired
    assert head.pairing.code_length == 4 and head.pairing.attempts_left == 5
    await head.close()


async def test_pairing_stores_token_and_reconnect_skips_pairing(sim, store):
    first = await Head.connect("127.0.0.1", sim.port, client="t", store=store)
    welcome = await first.pair("0000")
    assert welcome.device.platform == "sim"
    assert set(welcome.themes) == {"cartoon", "minimal", "halloween"}
    assert store.get(first.key) == welcome.token
    await first.close()

    second = await Head.connect("127.0.0.1", sim.port, client="t", store=store)
    assert second.paired and second.token == welcome.token
    await second.close()


async def test_wrong_codes_lock_pairing_after_five(sim, store):
    head = await Head.connect("127.0.0.1", sim.port, client="t", store=store)
    for left in (4, 3, 2, 1):
        with pytest.raises(HeadError) as err:
            await head.pair("9999")
        assert err.value.code == "unauthorized" and f"{left} attempts left" in err.value.message
    with pytest.raises(HeadError) as err:
        await head.pair("9999")
    assert err.value.code == "rate_limited"
    with pytest.raises(HeadError) as err:
        await head.pair("0000")  # even the right code is refused while locked
    assert err.value.code == "rate_limited"
    await head.close()


async def test_major_version_mismatch_is_unsupported(sim):
    [reply] = await raw(sim, {"type": "hello", "client": "old", "protocol_version": "1.0.0"})
    assert reply["code"] == "unsupported"


async def test_schema_violations_are_invalid_params(head):
    with pytest.raises(HeadError) as err:
        await head.face.set_emotion("happy", 1.5)
    assert err.value.code == "invalid_params" and "maximum" in err.value.message
    with pytest.raises(HeadError) as err:
        await head.command("face.look_at", frame="screen", x=0.2)  # y missing
    assert err.value.code == "invalid_params"
    with pytest.raises(HeadError) as err:
        await head.command("face.set_theme", name="cartoon", colour="red")
    assert err.value.code == "invalid_params"


async def test_unknown_and_device_only_types_are_unsupported(head):
    for type_ in ("face.dance", "status"):
        with pytest.raises(HeadError) as err:
            await head.command(type_)
        assert err.value.code == "unsupported"


# --- face and display --------------------------------------------------------


async def test_theme_and_emotion_show_in_status(head):
    await head.face.set_theme("halloween")
    await head.face.set_emotion("scared")
    status = await head.system.status()
    assert (status.theme, status.emotion, status.view) == ("halloween", "scared", "face")
    assert status.dev_mode and status.clients == 1


async def test_unknown_theme_is_rejected(head):
    with pytest.raises(HeadError) as err:
        await head.face.set_theme("nope")
    assert err.value.code == "invalid_params" and "unknown theme" in err.value.message


async def test_unknown_emotion_falls_back_to_neutral_with_warning(head):
    await head.face.set_emotion("cackle")  # a halloween extra; cartoon lacks it
    assert (await head.system.status()).emotion == "neutral"
    logs = await head.system.logs(20, "warning")
    assert any("emotion cackle not in theme cartoon" in e.message for e in logs)


async def test_face_list(head):
    result = await head.face.list()
    assert result.active == "cartoon"
    halloween = next(t for t in result.themes if t.name == "halloween")
    assert halloween.extras == ["cackle"] and len(halloween.expressions) == 28


async def test_look_at_and_blink(head, sim):
    await head.face.look_at(0.8, -0.5)
    await head.face.look_at(30, 10, frame="head", duration_ms=100)
    await head.face.blink()
    await asyncio.sleep(0.4)
    gaze = await sim.face._call("() => [window.openhead.params().gaze_x, window.openhead.params().gaze_y]")
    assert abs(gaze[0]) < 0.1 and abs(gaze[1]) < 0.1  # back to centre after duration_ms


async def test_envelope_stream_opens_mouth(head, sim):
    for _ in range(6):
        await head.face.envelope(0.9)
        await asyncio.sleep(0.04)
    assert await sim.face._call("() => window.openhead.params().open") > 0.5


async def test_display_image_overlay_and_timed_return(head):
    await head.display.show_image(PNG_1PX, overlay="face-corner", duration_ms=300)
    status = await head.system.status()
    assert (status.view, status.overlay) == ("image", "face-corner")
    await asyncio.sleep(0.6)
    status = await head.system.status()
    assert (status.view, status.overlay) == ("face", "none")


async def test_display_web_requires_http(head):
    with pytest.raises(HeadError) as err:
        await head.display.show_web("data:image/png;base64,AAAA")
    assert err.value.code == "invalid_params"


# --- system ------------------------------------------------------------------


async def test_screenshot_url_needs_token(head, sim):
    png = await head.system.screenshot(0.5)
    assert png.startswith(b"\x89PNG")
    result = await head.command("system.screenshot")
    assert result["width"] == 844 and result["height"] == 390
    with pytest.raises(urllib.error.HTTPError) as err:
        await asyncio.to_thread(urllib.request.urlopen, result["url"])
    assert err.value.code == 401


async def test_screenshot_inline(head):
    result = await head.command("system.screenshot", delivery="inline", scale=0.25)
    assert base64.b64decode(result["png_base64"]).startswith(b"\x89PNG")


async def test_dev_features_need_dev_mode(store):
    async with SimServer(host="127.0.0.1", port=0, mdns=False, dev_mode=False,
                         pairing_code="123456", validate_outgoing=True) as sim:
        head = await Head.connect("127.0.0.1", sim.port, client="t", store=store)
        assert head.pairing.code_length == 6
        await head.pair("123456")
        for call in (head.system.screenshot(), head.system.logs(), head.system.diagnostics(),
                     head.system.set_setting("name", "x")):
            with pytest.raises(HeadError) as err:
                await call
            assert err.value.code == "dev_mode_required"
        assert (await head.system.settings())["name"] == "openhead-sim"
        await head.close()
        assert sim.violations == []


async def test_settings_and_diagnostics(head):
    settings = await head.system.set_setting("mount_offset", [0, 0, 0.7071068, 0.7071068])
    assert settings["mount_offset"][2] == pytest.approx(0.7071068)
    with pytest.raises(HeadError):
        await head.system.set_setting("mount_offset", [1, 2])
    with pytest.raises(HeadError):
        await head.system.set_setting("unknown_key", 1)
    diagnostics = await head.system.diagnostics()
    assert diagnostics.thermal_state == "nominal"


async def test_modes(head):
    assert await head.mode.get() == "idle"
    assert (await head.system.status()).faces is None  # no camera, no count
    for mode in ("capture", "sensing", "idle"):
        await head.mode.set(mode)
        assert await head.mode.get() == mode


async def test_camera_view_switches_to_capture_and_streams_faces(head):
    await head.display.show_camera("camcorder", overlay="face-corner")
    status = await head.system.status()
    assert (status.view, status.overlay, status.mode) == ("camera", "face-corner", "capture")
    async with head.subscribe("faces", 15) as sub:
        msg = await anext(sub)
        while not msg.faces:
            msg = await anext(sub)
    assert msg.source == "sim" and all(f.box for f in msg.faces)
    assert (await head.face.list()).huds[0].name == "boot"
    with pytest.raises(HeadError) as err:
        await head.display.show_camera("nope")
    assert err.value.code == "invalid_params"
    await head.mode.set("idle")
    assert (await head.system.status()).view == "face"  # idle closes the camera view


async def test_sensing_streams_pose_and_one_face_without_box(head):
    with pytest.raises(HeadError):  # following a face needs a camera mode
        await head.face.look_at_face()
    await head.mode.set("sensing")
    async with head.subscribe("pose", 30) as sub:
        pose = await anext(sub)
    assert pose.frame == "world" and len(pose.position) == 3
    async with head.subscribe("faces", 15) as sub:
        faces = await anext(sub)
    assert len(faces.faces) == 1 and faces.faces[0].box is None and faces.faces[0].distance_m
    await head.face.look_at_face()
    await head.mode.set("idle")



async def test_gps_and_env_stream_in_any_mode(head):
    async with head.subscribe("gps", 5) as sub:
        assert sub.rate_hz == 1
        gps = await anext(sub)
    assert 59 < gps.lat < 60 and 18 < gps.lon < 19 and gps.h_accuracy_m > 0
    async with head.subscribe("env", 10, fields=["pressure_kpa", "heading_deg"]) as sub:
        env = await anext(sub)
    assert 90 < env.pressure_kpa < 110 and 0 <= env.heading_deg <= 360
    assert env.magnetic_field_ut is None  # only the fields asked for


# --- streams -----------------------------------------------------------------


async def test_imu_stream_is_clamped_and_physical(head):
    samples = []
    async with head.subscribe("imu", 500) as sub:
        assert sub.rate_hz == 100
        async for sample in sub:
            samples.append(sample)
            if len(samples) == 30:
                break
    for s in samples:
        assert isinstance(s, models.Imu)
        assert math.isclose(math.hypot(*s.q), 1, abs_tol=1e-4)
        assert math.isclose(math.hypot(*s.accel), 9.81, abs_tol=0.01)
        assert s.accel[1] > 9  # upright: specific force points up (+y)
    span = samples[-1].sensor_time_s - samples[0].sensor_time_s
    assert 0.2 < span < 0.6  # ~100 Hz


async def test_status_stream_with_field_filter(head):
    async with head.subscribe("status", 5, fields=["theme", "view"]) as sub:
        assert sub.rate_hz == 1
        first = await sub.__anext__()
    assert first.theme == "cartoon" and first.view == "face"
    assert first.model_dump(exclude_none=True).keys() >= {"type", "ts", "seq", "theme", "view"}


async def test_log_stream_references_commands(head):
    async with head.subscribe("log") as sub:
        await head.face.set_theme("minimal")
        seen = []
        async for entry in sub:
            seen.append(entry)
            if "theme=minimal" in entry.message:
                break
    received = [e for e in seen if e.message.startswith("recv face.set_theme")]
    assert received and received[0].seq_ref is not None


async def test_client_reconnects_and_resubscribes(head, sim):
    async with head.subscribe("imu", 50) as sub:
        await sub.__anext__()
        for session in list(sim.sessions):
            await session.ws.close()
        sample = await asyncio.wait_for(sub.__anext__(), 10)
        assert isinstance(sample, models.Imu)
    assert head.paired
    await head.face.blink()  # commands work on the new connection
