"""Upload the App Store screenshots and app preview to the version being prepared.

    uv run --project python python tools/appstore_media.py [--dry-run]

apps/ios/appstore/screenshots/iphone-6.9/*.png -> 6.9" iPhone set (APP_IPHONE_67)
apps/ios/appstore/screenshots/ipad-13/*.png    -> 13" iPad set (APP_IPAD_PRO_3GEN_129)
apps/ios/appstore/previews/iphone-6.9-landscape.mp4 -> 6.9" iPhone app preview (IPHONE_67)

Each set is replaced: what is there is deleted, then the files are uploaded in name order
(reserve, upload the parts App Store Connect asks for, commit with an MD5). Nothing is
submitted for review. Uses the API key in .env (tools/apple_setup.py).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import httpx
from apple_setup import Asc, read_env

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "apps" / "ios" / "appstore"
SCREENSHOTS = {"iphone-6.9": "APP_IPHONE_67", "ipad-13": "APP_IPAD_PRO_3GEN_129"}
PREVIEWS = {"iphone-6.9-landscape.mp4": "IPHONE_67"}


def upload(asc: Asc, kind: str, set_kind: str, set_id: str, path: Path, extra: dict | None = None) -> str:
    """Reserve, upload and commit one file; returns the asset id."""
    data = path.read_bytes()
    reserved = asc.request("POST", f"/{kind}", json={"data": {
        "type": kind, "attributes": {"fileName": path.name, "fileSize": len(data), **(extra or {})},
        "relationships": {set_kind[:-1]: {"data": {"type": set_kind, "id": set_id}}}}})["data"]
    for op in reserved["attributes"]["uploadOperations"]:
        part = data[op["offset"]:op["offset"] + op["length"]]
        headers = {h["name"]: h["value"] for h in op.get("requestHeaders") or []}
        r = httpx.request(op["method"], op["url"], content=part, headers=headers, timeout=120)
        r.raise_for_status()
    asc.request("PATCH", f"/{kind}/{reserved['id']}", json={"data": {
        "type": kind, "id": reserved["id"],
        "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
    return reserved["id"]


def ensure_set(asc: Asc, loc_id: str, set_kind: str, type_attr: str, type_value: str, dry: bool) -> str | None:
    sets = asc.request("GET", f"/appStoreVersionLocalizations/{loc_id}/{set_kind}")["data"]
    found = [s for s in sets if s["attributes"][type_attr] == type_value]
    if found:
        return found[0]["id"]
    if dry:
        return None
    return asc.request("POST", f"/{set_kind}", json={"data": {
        "type": set_kind, "attributes": {type_attr: type_value},
        "relationships": {"appStoreVersionLocalization": {"data": {
            "type": "appStoreVersionLocalizations", "id": loc_id}}}}})["data"]["id"]


def wait_states(asc: Asc, kind: str, ids: list[str], timeout_s: int = 300) -> None:
    """Wait until App Store Connect has processed the uploads; report failures."""
    deadline = time.time() + timeout_s
    pending = set(ids)
    while pending and time.time() < deadline:
        for asset_id in list(pending):
            attrs = asc.request("GET", f"/{kind}/{asset_id}")["data"]["attributes"]
            state = (attrs.get("assetDeliveryState") or {}).get("state")
            if state == "COMPLETE":
                pending.discard(asset_id)
            elif state == "FAILED":
                errors = (attrs.get("assetDeliveryState") or {}).get("errors")
                print(f"  {attrs.get('fileName')}: FAILED {errors}")
                pending.discard(asset_id)
        if pending:
            time.sleep(5)
    if pending:
        print(f"  {len(pending)} still processing; check App Store Connect")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    env = read_env()
    asc = Asc(env)
    app = env["ASC_APP_ID"]
    versions = [v for v in asc.request("GET", f"/apps/{app}/appStoreVersions")["data"]
                if v["attributes"]["appStoreState"] == "PREPARE_FOR_SUBMISSION"]
    if not versions:
        print("no version in preparation")
        return 1
    locale = asc.request("GET", f"/apps/{app}", params={"fields[apps]": "primaryLocale"})["data"]["attributes"]["primaryLocale"]
    loc = next(x for x in asc.request("GET", f"/appStoreVersions/{versions[0]['id']}/appStoreVersionLocalizations")["data"]
               if x["attributes"]["locale"] == locale)

    for folder, display in SCREENSHOTS.items():
        files = sorted((STORE / "screenshots" / folder).glob("*.png"))[:10]
        print(f"{display}: {len(files)} screenshots from {folder}")
        if args.dry_run:
            continue
        set_id = ensure_set(asc, loc["id"], "appScreenshotSets", "screenshotDisplayType", display, False)
        for old in asc.request("GET", f"/appScreenshotSets/{set_id}/appScreenshots")["data"]:
            asc.request("DELETE", f"/appScreenshots/{old['id']}")
        ids = [upload(asc, "appScreenshots", "appScreenshotSets", set_id, f) for f in files]
        wait_states(asc, "appScreenshots", ids)

    for name, preview_type in PREVIEWS.items():
        path = STORE / "previews" / name
        if not path.exists():
            continue
        print(f"{preview_type}: preview {name}")
        if args.dry_run:
            continue
        set_id = ensure_set(asc, loc["id"], "appPreviewSets", "previewType", preview_type, False)
        for old in asc.request("GET", f"/appPreviewSets/{set_id}/appPreviews")["data"]:
            asc.request("DELETE", f"/appPreviews/{old['id']}")
        preview = upload(asc, "appPreviews", "appPreviewSets", set_id, path,
                         {"mimeType": "video/mp4", "previewFrameTimeCode": "00:00:05:00"})
        wait_states(asc, "appPreviews", [preview], timeout_s=900)
    if args.dry_run:
        print("dry run: nothing uploaded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
