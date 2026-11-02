"""Speech (0.4): cue parsing, the simulator's voice and ears, and the MCP tools."""

import asyncio

import pytest
from mcp import Client

from openhead.mcp.server import HeadLink, build_server
from openhead.speech import parse, spoken_text
from openhead.tokens import TokenStore

JOKE = "[happy] Why did the robot go on holiday? [pause 0.3] It needed to recharge! [laugh] [serious] [nod] Meeting soon."


def test_parse_cues_into_segments():
    segs = parse(JOKE)
    assert segs == [
        {"emotion": "happy"}, {"say": "Why did the robot go on holiday?"},
        {"action": "pause", "seconds": 0.3}, {"say": "It needed to recharge!"},
        {"action": "laugh"}, {"emotion": "focused"}, {"gesture": "nod"}, {"say": "Meeting soon."},
    ]
    assert spoken_text(segs) == "Why did the robot go on holiday? It needed to recharge! Meeting soon."


def test_parse_intensity_plain_text_and_limits():
    assert parse("[sad 0.4] Oh no.") == [{"emotion": "sad", "intensity": 0.4}, {"say": "Oh no."}]
    assert parse("Just words.") == [{"say": "Just words."}]
    assert parse("[pause 9]")[0]["seconds"] == 5.0
    long = parse("word " * 600)
    assert all(len(s["say"]) <= 2000 for s in long) and len(long) == 2
    with pytest.raises(ValueError):
        parse("   ")


async def test_say_runs_segments_in_order_with_cues(head, sim):
    seen = []
    async with head.subscribe("speech") as sub:
        uid = await head.speech.say("[happy] Hi! [laugh] [nod] [sad 0.5] Bye.")

        async def until_end():
            async for msg in sub:
                seen.append(msg)
                if msg.event == "say_end":
                    return
        await asyncio.wait_for(until_end(), 10)
    assert seen[0].event == "say_start" and seen[-1].interrupted is False
    cues = [(m.cue_type, m.cue) for m in seen if m.event == "cue"]
    assert cues == [("emotion", "happy"), ("action", "laugh"), ("gesture", "nod"), ("emotion", "sad")]
    assert all(m.utterance_id == uid for m in seen)
    assert (await sim.face.state())["emotion"] == "sad"   # the last cue holds; laugh went back


async def test_a_new_utterance_interrupts_and_stop_ends(head):
    seen = []
    async with head.subscribe("speech") as sub:
        first = await head.speech.say("This is a long sentence that takes a few seconds to say out loud.")
        await asyncio.sleep(0.3)
        second = await head.speech.say("Short.")

        async def until_second_ends():
            async for msg in sub:
                seen.append(msg)
                if msg.event == "say_end" and msg.utterance_id == second:
                    return
        await asyncio.wait_for(until_second_ends(), 10)
    ends = {m.utterance_id: m.interrupted for m in seen if m.event == "say_end"}
    assert ends == {first: True, second: False}


async def test_listen_and_auto_expressions(head, sim):
    result = await head.speech.listen(True)
    assert result["listening"] is True
    heard = []
    async with head.subscribe("speech") as sub:
        await sim.hear("tell me a joke")

        async def until_heard():
            async for msg in sub:
                heard.append(msg)
                if msg.event == "heard":
                    return
        await asyncio.wait_for(until_heard(), 5)
    assert heard[0].event == "partial" and heard[-1].text == "tell me a joke"
    assert (await sim.face.state())["emotion"] == "thinking"
    await head.speech.say("Here goes.")               # thinking ends when it starts to speak
    await asyncio.sleep(0.3)
    assert (await sim.face.state())["emotion"] == "neutral"


async def test_mcp_say_and_listen(sim, tmp_path):
    link = HeadLink(f"127.0.0.1:{sim.port}", client="pytest-mcp", store=TokenStore(tmp_path / "t.json"))
    try:
        async with Client(build_server(link)) as client:
            assert not (await client.call_tool("pair", {"code": "0000"})).is_error
            r = await client.call_tool("say", {"text": "[happy] Hello there! [laugh]"})
            assert not r.is_error and r.content[0].text == "said: Hello there!"
            r = await client.call_tool("listen", {"timeout_s": 0.5})   # starts listening, nobody spoke
            assert not r.is_error and r.content[0].text == ""

            async def speak_later():
                await asyncio.sleep(0.3)
                await sim.hear("what time is it")
            task = asyncio.create_task(speak_later())
            r = await client.call_tool("listen", {"timeout_s": 5})
            await task
            assert r.content[0].text == "what time is it"
            await sim.hear("hello again")                         # said between two calls: kept
            await asyncio.sleep(0.3)
            r = await client.call_tool("listen", {"timeout_s": 1})
            assert r.content[0].text == "hello again"
    finally:
        await link.close()
