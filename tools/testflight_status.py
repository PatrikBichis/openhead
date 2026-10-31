"""Show the latest TestFlight builds and their processing state (App Store Connect API).

    uv run --project python python tools/testflight_status.py [--wait BUILD_NUMBER]

The upload workflow does not wait for Apple's processing (to save macOS minutes); this
checks it locally instead. Uses the API key from .env.
"""

from __future__ import annotations

import argparse
import sys
import time

from apple_setup import Asc, read_env


def builds(asc: Asc, app_id: str) -> list[dict]:
    data = asc.request("GET", "/builds", params={
        "filter[app]": app_id, "sort": "-uploadedDate", "limit": 10,
        "fields[builds]": "version,uploadedDate,processingState,expirationDate,expired",
        "include": "preReleaseVersion", "fields[preReleaseVersions]": "version",
    })
    versions = {v["id"]: v["attributes"]["version"] for v in data.get("included", [])}
    rows = []
    for b in data["data"]:
        rel = b["relationships"]["preReleaseVersion"]["data"]
        rows.append({"build": b["attributes"]["version"],
                     "version": versions.get(rel["id"], "?") if rel else "?",
                     "state": b["attributes"]["processingState"],
                     "uploaded": b["attributes"]["uploadedDate"][:16].replace("T", " ")})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wait", metavar="BUILD", help="poll until this build number is VALID")
    args = parser.parse_args()
    env = read_env()
    asc = Asc(env)
    while True:
        rows = builds(asc, env["ASC_APP_ID"])
        target = next((r for r in rows if r["build"] == args.wait), None) if args.wait else None
        if not args.wait or (target and target["state"] in ("VALID", "FAILED", "INVALID")):
            break
        print(f"build {args.wait}: {target['state'] if target else 'not visible yet'}; waiting...",
              flush=True)
        time.sleep(30)
    for r in rows:
        print(f"{r['version']:<8} ({r['build']:>4})  {r['state']:<11} uploaded {r['uploaded']}")
    return 0 if not args.wait or target["state"] == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
