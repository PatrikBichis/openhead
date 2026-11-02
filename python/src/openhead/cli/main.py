"""`openhead` command line: talk to a head, run scenarios, start the simulator."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import logging
import os
import sys
from pathlib import Path

from ..client import Head, HeadError, discover, resolve_device
from ..protocol import DEFAULT_PORT

EPILOG = """examples:
  openhead sim                                   simulated head with a window (pairing code 0000)
  openhead pair 0000 --device localhost
  openhead pair --device 192.168.1.20            connects (the head shows a code), then asks for it
  openhead emotion curious --device localhost
  openhead show clip.mp4 --overlay face-corner      play a local video (served from here)
  openhead subtitle "Hello there" --mouth           text on screen, mouth moving
  openhead say "[happy] Hi! [laugh] [sad 0.5] Bye."  speak with the head's voice (0.4), cues in brackets
  openhead listen -n 3                              print what the head hears (speech to text)
  openhead camera hunter --follow                   camera view with HUD; the eyes follow a face
  openhead watch faces -n 5                         print the faces stream
  openhead hud --set speed=0.4 --line "SPEED {speed} M/S" --widget compass
  openhead screenshot -o face.png --device localhost
  openhead run scenarios/smoke.yaml --device localhost

--device defaults to $OPENHEAD_DEVICE (also read from .env), else 'auto' (mDNS discovery)."""


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    parser = argparse.ArgumentParser(prog="openhead", description=__doc__, epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", default=os.environ.get("OPENHEAD_DEVICE", "auto"),
                        help="host[:port], or 'auto' to discover over mDNS")
    parser.add_argument("--client", default=f"openhead-cli@{_hostname()}",
                        help="client name shown on the device")
    parser.add_argument("-v", "--verbose", action="store_true")
    # The same options are accepted after the command too (`openhead pair --device ...`).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--device", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    common.add_argument("--client", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    common.add_argument("-v", "--verbose", action="store_true", default=argparse.SUPPRESS,
                        help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="command")

    p = sub.add_parser("discover", parents=[common], help="list heads on the network")
    p.add_argument("--timeout", type=float, default=2.0)

    p = sub.add_parser("pair", parents=[common], help="pair with the code shown on the head")
    p.add_argument("code", nargs="?",
                   help="the code on the head; omit to connect first (shows the code) and type it")

    sub.add_parser("status", parents=[common], help="show device status")

    p = sub.add_parser("screenshot", parents=[common], help="save what is on screen (dev mode)")
    p.add_argument("-o", "--output", default="screenshot.png")
    p.add_argument("--scale", type=float)

    p = sub.add_parser("logs", parents=[common], help="show the device log (dev mode)")
    p.add_argument("-n", type=int, default=50)
    p.add_argument("--level")
    p.add_argument("-f", "--follow", action="store_true", help="keep streaming new lines")

    p = sub.add_parser("emotion", parents=[common], help="set an emotion")
    p.add_argument("name")
    p.add_argument("--intensity", type=float, default=1.0)
    p.add_argument("--duration-ms", type=int)

    p = sub.add_parser("theme", parents=[common], help="set the face theme")
    p.add_argument("name")

    sub.add_parser("themes", parents=[common], help="list themes and their expressions")

    p = sub.add_parser("show", parents=[common],
                       help="show an image or video (URL or file), a web page, or 'face'")
    p.add_argument("source")
    p.add_argument("--loop", action="store_true", help="video: play again at the end")
    p.add_argument("--muted", action="store_true", help="video: no sound")
    p.add_argument("--web", action="store_true", help="treat source as a web page URL")
    p.add_argument("--overlay", choices=["none", "face-corner"], default="none")
    p.add_argument("--duration-ms", type=int)

    p = sub.add_parser("camera", parents=[common], help="show the front camera with a HUD (mode capture)")
    p.add_argument("hud", nargs="?", default="hunter", help="HUD theme (see `themes`), or none")
    p.add_argument("--overlay", choices=["none", "face-corner"], default="none")
    p.add_argument("--follow", action="store_true", help="the eyes follow the locked face")

    p = sub.add_parser("hud", parents=[common], help="put your own values and lines on the camera HUD")
    p.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                   help="a value for templates, e.g. --set speed=0.4 (repeatable)")
    p.add_argument("--line", action="append", default=[], help='a text line, e.g. --line "SPEED {speed} M/S"')
    p.add_argument("--at", default="bottom-left",
                   choices=["top-left", "top-right", "bottom-left", "bottom-right", "left"])
    p.add_argument("--widget", action="append", default=[], choices=["compass", "horizon", "battery"])
    p.add_argument("--clear", action="store_true", help="remove what was added")

    p = sub.add_parser("mode", parents=[common], help="show or set who owns the cameras")
    p.add_argument("mode", nargs="?", choices=["idle", "capture", "sensing"])

    p = sub.add_parser("watch", parents=[common], help="print a stream: faces, pose, gps, env, imu or status")
    p.add_argument("topic", choices=["faces", "pose", "gps", "env", "imu", "status"])
    p.add_argument("--rate", type=float)
    p.add_argument("-n", type=int, default=0, help="stop after n messages (0: until Ctrl+C)")

    p = sub.add_parser("subtitle", parents=[common], help="show text on top of the screen")
    p.add_argument("text", nargs="*", help="omit with --mode clear")
    p.add_argument("--mode", choices=["replace", "append", "clear"], default="replace")
    p.add_argument("--position", choices=["bottom", "top"])
    p.add_argument("--duration-ms", type=int)
    p.add_argument("--mouth", action="store_true", help="move the mouth with the text")

    p = sub.add_parser("say", parents=[common], help="speak with the head's voice; cues like [happy] [laugh]")
    p.add_argument("text", nargs="+")
    p.add_argument("--voice", help="language (en-US, sv-SE) or voice identifier")
    p.add_argument("--rate", type=float, help="0.5-2, relative to normal")
    p.add_argument("--no-subtitle", action="store_true")

    p = sub.add_parser("listen", parents=[common], help="print what the head hears (speech to text)")
    p.add_argument("--locale", default="en-US")
    p.add_argument("-n", type=int, default=0, help="stop after n utterances (0: until Ctrl+C)")
    p.add_argument("--partial", action="store_true", help="also print the words as they come")

    p = sub.add_parser("run", parents=[common], help="run YAML scenarios")
    p.add_argument("scenarios", nargs="+", type=Path)
    p.add_argument("--out", type=Path, help="report directory (default scenario-reports/...)")
    p.add_argument("--compare", action="store_true",
                   help="compare screenshots with scenarios/golden/<name>/ (simulator)")
    p.add_argument("--update-golden", action="store_true")

    p = sub.add_parser("sim", parents=[common], help="start the desktop simulator")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--name", default="openhead-sim")
    p.add_argument("--theme", default="cartoon")
    p.add_argument("--size", default="844x390",
                   help="viewport WxH in points (default iPhone 12 landscape)")
    p.add_argument("--no-dev", action="store_true", help="dev mode off (random pairing code)")
    p.add_argument("--no-mdns", action="store_true")
    p.add_argument("--tokens", type=Path, default=Path.home() / ".openhead" / "sim-device-tokens.json",
                   help="where the simulator keeps paired clients")
    p.add_argument("--idle", action=argparse.BooleanOptionalAction, default=None,
                   help="idle motion (default: on with a window, off headless)")

    p = sub.add_parser("mcp", parents=[common], help="MCP server (stdio, or HTTP) exposing the head to agents")
    p.add_argument("--selftest", action="store_true",
                   help="run every tool against a headless simulator and exit")
    p.add_argument("--http", metavar="[HOST:]PORT",
                   help="serve Streamable HTTP at http://HOST:PORT/mcp instead of stdio (HOST defaults to 127.0.0.1)")
    p.add_argument("--token", default=os.environ.get("OPENHEAD_MCP_TOKEN"),
                   help="bearer token clients must send with --http; required on a network address "
                        "(default $OPENHEAD_MCP_TOKEN)")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose or args.cmd == "sim" else logging.WARNING,
                        format="%(asctime)s %(name)s %(message)s", datefmt="%H:%M:%S")
    try:
        return asyncio.run(_dispatch(args))
    except HeadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except (ConnectionError, OSError, TimeoutError) as exc:
        print(f"error: cannot reach head: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


async def _dispatch(args: argparse.Namespace) -> int:
    if args.cmd == "sim":
        return await _sim(args)
    if args.cmd == "discover":
        devices = await discover(args.timeout)
        for d in devices:
            print(f"{d.name}\t{d.address}")
        if not devices:
            print("no heads found", file=sys.stderr)
        return 0 if devices else 1
    if args.cmd == "mcp":
        try:
            from ..mcp.selftest import selftest
            from ..mcp.server import serve_http, serve_stdio
        except ImportError as exc:
            print(f"the MCP server needs the [mcp] extra: {exc}", file=sys.stderr)
            return 1
        if args.selftest:
            return await selftest()
        client = args.client.replace("openhead-cli", "openhead-mcp")
        if args.http:
            host, _, port = args.http.rpartition(":")
            await serve_http(args.device, client, host or "127.0.0.1", int(port), args.token)
        else:
            await serve_stdio(args.device, client)
        return 0

    host, port = await resolve_device(args.device)
    head = await Head.connect(host, port, client=args.client, auto_reconnect=False)
    async with head:
        if args.cmd == "pair":
            if head.paired:
                print(f"already paired with {head.welcome.device.name} ({head.key})")
                return 0
            code = args.code
            if not code:
                # Our hello has made the head show a code; read it on the same connection.
                seconds = head.pairing.expires_in_ms // 1000 if head.pairing else 60
                prompt = f"code shown on {head.key} (valid {seconds} s): "
                code = (await asyncio.to_thread(input, prompt)).strip()
            welcome = await head.pair(code)
            print(f"paired with {welcome.device.name} ({head.key}); token saved")
            return 0
        if not head.paired:
            hint = head.pairing.code_hint if head.pairing else ""
            print(f"not paired with {head.key}: run `openhead pair --device {args.device}`"
                  f" ({hint})", file=sys.stderr)
            return 1
        return await _command(head, args)


async def _command(head: Head, args: argparse.Namespace) -> int:
    match args.cmd:
        case "status":
            for k, v in (await head.system.status()).model_dump(exclude_none=True).items():
                print(f"{k:<14}{v}")
        case "screenshot":
            Path(args.output).write_bytes(await head.system.screenshot(args.scale))
            print(args.output)
        case "logs":
            for e in await head.system.logs(args.n, args.level):
                print(f"{e.level:<7} {e.subsystem:<9} {e.message}")
            if args.follow:
                async for e in head.subscribe("log"):
                    print(f"{e.level:<7} {e.subsystem:<9} {e.message}", flush=True)
        case "emotion":
            await head.face.set_emotion(args.name, args.intensity, duration_ms=args.duration_ms)
        case "theme":
            await head.face.set_theme(args.name)
        case "themes":
            result = await head.face.list()
            for t in result.themes:
                active = "*" if t.name == result.active else " "
                extras = f" + {', '.join(t.extras)}" if t.extras else ""
                print(f"{active} {t.name:<10} {t.version:<7} {len(t.expressions)} expressions{extras}")
        case "show":
            if args.source == "face":
                await head.display.show_face()
            elif args.web:
                await head.display.show_web(args.source, overlay=args.overlay,
                                            duration_ms=args.duration_ms)
            elif args.source.lower().endswith(VIDEO_SUFFIXES):
                return await _show_video(head, args)
            else:
                source = args.source
                if not source.startswith(("http://", "https://", "data:")):
                    source = Path(source).read_bytes()
                await head.display.show_image(source, overlay=args.overlay,
                                              duration_ms=args.duration_ms)
        case "camera":
            await head.display.show_camera(args.hud, overlay=args.overlay)
            if args.follow:
                await head.face.look_at_face()
        case "hud":
            values = {}
            for item in args.set:
                key, _, raw = item.partition("=")
                try:
                    values[key] = float(raw) if "." in raw else int(raw)
                except ValueError:
                    values[key] = raw
            await head.display.hud(values or None,
                                   blocks=[{"at": args.at, "lines": args.line}] if args.line else None,
                                   widgets=[{"type": w} for w in args.widget] or None, clear=args.clear)
        case "mode":
            if args.mode:
                await head.mode.set(args.mode)
            print(await head.mode.get())
        case "watch":
            count = 0
            async with head.subscribe(args.topic, args.rate) as sub:
                async for msg in sub:
                    print(json.dumps(msg.model_dump(exclude_none=True, exclude={"type"})), flush=True)
                    count += 1
                    if args.n and count >= args.n:
                        break
        case "subtitle":
            await head.display.subtitle(" ".join(args.text), mode=args.mode, position=args.position,
                                        duration_ms=args.duration_ms, mouth=args.mouth)
        case "say":
            async with head.subscribe("speech") as sub:
                uid = await head.speech.say(" ".join(args.text), voice=args.voice, rate=args.rate,
                                            subtitle=False if args.no_subtitle else None)
                async for msg in sub:
                    if msg.event == "cue" and msg.utterance_id == uid:
                        print(f"  [{msg.cue}]")
                    if msg.event == "say_end" and msg.utterance_id == uid:
                        print("interrupted" if msg.interrupted else "done")
                        break
        case "listen":
            result = await head.speech.listen(True, locale=args.locale)
            where = "on the device" if result.get("on_device") else "with Apple's server"
            print(f"listening ({result.get('locale', args.locale)}, {where}); Ctrl+C stops", flush=True)
            count = 0
            try:
                async with head.subscribe("speech") as sub:
                    async for msg in sub:
                        if msg.event == "partial" and args.partial:
                            print(f"  … {msg.text}", flush=True)
                        elif msg.event == "heard":
                            conf = f" ({msg.confidence:.2f})" if msg.confidence is not None else ""
                            print(f"> {msg.text}{conf}", flush=True)
                            count += 1
                            if args.n and count >= args.n:
                                break
            finally:
                await head.speech.listen(False)
        case "run":
            from ..scenario import run_scenario

            failed = 0
            for path in args.scenarios:
                golden = path.parent / "golden" if args.compare or args.update_golden else None
                out = args.out / path.stem if args.out else None
                report = await run_scenario(head, path, out_dir=out, golden_dir=golden,
                                            update_golden=args.update_golden)
                print(report.text())
                failed += not report.passed
            return 1 if failed else 0
    return 0


async def _sim(args: argparse.Namespace) -> int:
    try:
        from ..sim import SimConfig, SimServer
    except ImportError as exc:
        print(f"the simulator needs the [sim] extra: {exc}", file=sys.stderr)
        return 1
    w, _, h = args.size.partition("x")
    config = SimConfig(
        host=args.host, port=args.port, name=args.name, dev_mode=not args.no_dev,
        headless=args.headless, idle=args.idle, size=(int(w), int(h)), theme=args.theme,
        token_path=args.tokens, mdns=not args.no_mdns,
    )
    if config.dev_mode:
        print("dev mode: pairing code 0000", flush=True)
    with contextlib.suppress(asyncio.CancelledError):
        await SimServer(config).serve_forever()
    return 0


def _load_dotenv() -> None:
    """Take OPENHEAD_* from the nearest .env (cwd or a parent); the environment wins."""
    for folder in (Path.cwd(), *Path.cwd().parents):
        env = folder / ".env"
        if env.is_file():
            for line in env.read_text(encoding="utf-8").splitlines():
                key, sep, value = line.partition("=")
                key = key.strip()
                if sep and key.startswith("OPENHEAD_") and value.strip():
                    os.environ.setdefault(key, value.strip().strip('"'))
            return


VIDEO_SUFFIXES = (".mp4", ".m4v", ".mov", ".webm")


async def _show_video(head: Head, args: argparse.Namespace) -> int:
    """A video URL is shown as is; a local file is served from here until it has played."""
    from ..client import MediaServer

    if args.source.startswith(("http://", "https://")):
        await head.display.show_video(args.source, overlay=args.overlay, loop=args.loop,
                                      muted=args.muted, duration_ms=args.duration_ms)
        return 0
    async with MediaServer() as media:
        url = media.url_for(Path(args.source), head)
        await head.display.show_video(url, overlay=args.overlay, loop=args.loop, muted=args.muted,
                                      duration_ms=args.duration_ms)
        print(f"serving {args.source} until it has played (Ctrl+C stops)", flush=True)
        with contextlib.suppress(asyncio.CancelledError):
            while (await head.system.status()).view == "video":
                await asyncio.sleep(1)
    return 0


def _hostname() -> str:
    import socket

    return socket.gethostname().split(".")[0][:32]


if __name__ == "__main__":
    sys.exit(main())
