"""Upload the App Store screenshots and app preview to the version being prepared.

    uv run --project python python tools/appstore_media.py [screenshots] [creative] [previews] [--dry-run]

apps/ios/appstore/screenshots/iphone-6.9/*.png -> 6.9" iPhone set (APP_IPHONE_67)
apps/ios/appstore/screenshots/ipad-13/*.png    -> 13" iPad set (APP_IPAD_PRO_3GEN_129)
apps/ios/appstore/previews/iphone-6.9-landscape.mp4 -> 6.9" iPhone app preview (IPHONE_67)
apps/ios/appstore/creative/header.png          -> product page header (21:9, 3840 x 1646)
apps/ios/appstore/creative/search-results.png  -> search results (3:2, 1920 x 1280)

Default: all three. Each set is replaced: what is there is deleted, then the files are uploaded in name order
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
# Creative assets (2026): asset library images placed on the version's localization.
CREATIVE = {"header.png": "PRODUCT_PAGE_HEADER_ASSET", "search-results.png": "APP_STORE_SEARCH_RESULTS_ASSET"}


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


def upload_creative(asc: Asc, app: str, path: Path) -> str:
    """Upload a creative asset to the app's asset library; returns the image id."""
    data = path.read_bytes()
    reserved = asc.request("POST", "/appAssetLibraryImages", json={"data": {
        "type": "appAssetLibraryImages",
        "attributes": {"fileName": path.name, "fileSize": len(data), "category": "CREATIVE_ASSETS"},
        "relationships": {"assetLibrary": {"data": {"type": "appAssetLibraries", "id": app}}}}})["data"]
    for op in reserved["attributes"]["uploadOperations"]:
        part = data[op["offset"]:op["offset"] + op["length"]]
        headers = {h["name"]: h["value"] for h in op.get("requestHeaders") or []}
        httpx.request(op["method"], op["url"], content=part, headers=headers, timeout=120).raise_for_status()
    asc.request("PATCH", f"/appAssetLibraryImages/{reserved['id']}", json={"data": {
        "type": "appAssetLibraryImages", "id": reserved["id"], "attributes": {"uploaded": True}}})
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


def wait_image(asc: Asc, image: str, timeout_s: int = 300) -> None:
    """Asset library images report `state`; wait until processing has finished."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        attrs = asc.request("GET", f"/appAssetLibraryImages/{image}")["data"]["attributes"]
        state = attrs.get("state")
        if state not in ("AWAITING_UPLOAD", "UPLOAD_COMPLETE", "PROCESSING", None):
            print(f"  {attrs['fileName']}: {state}" + (f" {attrs['stateDetails']}" if attrs.get("stateDetails") else ""))
            return
        time.sleep(5)
    print("  still processing; check App Store Connect")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("what", nargs="*", choices=["screenshots", "creative", "previews"],
                        default=["screenshots", "creative", "previews"])
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

    for folder, display in SCREENSHOTS.items() if "screenshots" in args.what else []:
        files = sorted((STORE / "screenshots" / folder).glob("*.png"))[:10]
        print(f"{display}: {len(files)} screenshots from {folder}")
        if args.dry_run:
            continue
        set_id = ensure_set(asc, loc["id"], "appScreenshotSets", "screenshotDisplayType", display, False)
        for old in asc.request("GET", f"/appScreenshotSets/{set_id}/appScreenshots")["data"]:
            asc.request("DELETE", f"/appScreenshots/{old['id']}")
        ids = [upload(asc, "appScreenshots", "appScreenshotSets", set_id, f) for f in files]
        wait_states(asc, "appScreenshots", ids)

    for name, placement_type in CREATIVE.items() if "creative" in args.what else []:
        path = STORE / "creative" / name
        if not path.exists():
            continue
        print(f"{placement_type}: {name}")
        if args.dry_run:
            continue
        for old in asc.request("GET", f"/appStoreVersionLocalizations/{loc['id']}/placements")["data"]:
            if old["attributes"]["placementType"] == placement_type:
                asc.request("DELETE", f"/appAssetLibraryPlacements/{old['id']}")
        image = upload_creative(asc, app, path)
        asc.request("POST", "/appAssetLibraryPlacements", json={"data": {
            "type": "appAssetLibraryPlacements", "attributes": {"placementType": placement_type},
            "relationships": {
                "appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": loc["id"]}},
                "image": {"data": {"type": "appAssetLibraryImages", "id": image}}}}})
        wait_image(asc, image)

    for name, preview_type in PREVIEWS.items() if "previews" in args.what else []:
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
