"""`openhead` command line: talk to a head, run scenarios, start the simulator."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import sys
from pathlib import Path

from ..client import Head, HeadError, discover, resolve_device
from ..protocol import DEFAULT_PORT

EPILOG = """examples:
  openhead sim                                   simulated head with a window (pairing code 0000)
  openhead pair 0000 --device localhost
  openhead emotion curious --device localhost
  openhead screenshot -o face.png --device localhost
  openhead run scenarios/smoke.yaml --device localhost

--device defaults to $OPENHEAD_DEVICE, else 'auto' (mDNS discovery)."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openhead", description=__doc__, epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", default=os.environ.get("OPENHEAD_DEVICE", "auto"),
                        help="host[:port], or 'auto' to discover over mDNS")
    parser.add_argument("--client", default=f"openhead-cli@{_hostname()}",
                        help="client name shown on the device")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="command")

    p = sub.add_parser("discover", help="list heads on the network")
    p.add_argument("--timeout", type=float, default=2.0)

    p = sub.add_parser("pair", help="pair with the code shown on the head")
    p.add_argument("code")

    sub.add_parser("status", help="show device status")

    p = sub.add_parser("screenshot", help="save what is on screen (dev mode)")
    p.add_argument("-o", "--output", default="screenshot.png")
    p.add_argument("--scale", type=float)

    p = sub.add_parser("logs", help="show the device log (dev mode)")
    p.add_argument("-n", type=int, default=50)
    p.add_argument("--level")
    p.add_argument("-f", "--follow", action="store_true", help="keep streaming new lines")

    p = sub.add_parser("emotion", help="set an emotion")
    p.add_argument("name")
    p.add_argument("--intensity", type=float, default=1.0)
    p.add_argument("--duration-ms", type=int)

    p = sub.add_parser("theme", help="set the face theme")
    p.add_argument("name")

    sub.add_parser("themes", help="list themes and their expressions")

    p = sub.add_parser("show", help="show an image (URL or file), a web page, or 'face'")
    p.add_argument("source")
    p.add_argument("--web", action="store_true", help="treat source as a web page URL")
    p.add_argument("--overlay", choices=["none", "face-corner"], default="none")
    p.add_argument("--duration-ms", type=int)

    p = sub.add_parser("run", help="run YAML scenarios")
    p.add_argument("scenarios", nargs="+", type=Path)
    p.add_argument("--out", type=Path, help="report directory (default scenario-reports/...)")
    p.add_argument("--compare", action="store_true",
                   help="compare screenshots with scenarios/golden/<name>/ (simulator)")
    p.add_argument("--update-golden", action="store_true")

    p = sub.add_parser("sim", help="start the desktop simulator")
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

    p = sub.add_parser("mcp", help="MCP server (stdio) exposing the head to agents")
    p.add_argument("--selftest", action="store_true",
                   help="run every tool against a headless simulator and exit")

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
            from ..mcp.server import serve_stdio
        except ImportError as exc:
            print(f"the MCP server needs the [mcp] extra: {exc}", file=sys.stderr)
            return 1
        if args.selftest:
            return await selftest()
        await serve_stdio(args.device, args.client.replace("openhead-cli", "openhead-mcp"))
        return 0

    host, port = await resolve_device(args.device)
    head = await Head.connect(host, port, client=args.client, auto_reconnect=False)
    async with head:
        if args.cmd == "pair":
            if head.paired:
                print(f"already paired with {head.welcome.device.name} ({head.key})")
                return 0
            welcome = await head.pair(args.code)
            print(f"paired with {welcome.device.name} ({head.key}); token saved")
            return 0
        if not head.paired:
            hint = head.pairing.code_hint if head.pairing else ""
            print(f"not paired with {head.key}: run `openhead pair <code> --device {args.device}`"
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
            else:
                source = args.source
                if not source.startswith(("http://", "https://", "data:")):
                    source = Path(source).read_bytes()
                await head.display.show_image(source, overlay=args.overlay,
                                              duration_ms=args.duration_ms)
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


def _hostname() -> str:
    import socket

    return socket.gethostname().split(".")[0][:32]


if __name__ == "__main__":
    sys.exit(main())
