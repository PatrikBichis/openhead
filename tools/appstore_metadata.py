"""Push the store texts in apps/ios/appstore/metadata/ to App Store Connect.

    uv run --project python python tools/appstore_metadata.py [--dry-run] [--build N]

metadata/<locale>/     App Store page per language (en-US is the primary, sv-SE Swedish):
                       name, description, subtitle, promotional_text, keywords, support_url,
                       marketing_url, privacy_policy_url (the version being prepared and the
                       app info; a missing language is created; not submitted)
metadata/testflight/   beta_description (TestFlight app description) and whats_new
                       ("What to Test" for the newest build, or --build N)
metadata/app.json      release type and categories; with copyright.txt, age_rating.json and
                       review_notes.txt also the version number (protocol/VERSION) and its
                       newest valid build on the version being prepared

Only fields with a file are touched; nothing is submitted for review. Uses the API key in .env.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from apple_setup import Asc, read_env

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "apps" / "ios" / "appstore" / "metadata"
LIMITS = {"description": 4000, "subtitle": 30, "promotionalText": 170, "keywords": 100,
          "whatsNew": 4000}


def text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8").strip() if path.exists() else None


def fields(folder: Path, names: dict[str, str]) -> dict[str, str]:
    out = {}
    for file, attr in names.items():
        value = text(folder / f"{file}.txt")
        if value is None:
            continue
        if attr in LIMITS and len(value) > LIMITS[attr]:
            raise SystemExit(f"{folder.name}/{file}.txt: {len(value)} characters, limit {LIMITS[attr]}")
        out[attr] = value
    return out


class Sync:
    def __init__(self, asc: Asc, dry_run: bool):
        self.asc = asc
        self.dry_run = dry_run

    def upsert(self, kind: str, existing: dict | None, attrs: dict, create: dict, label: str) -> None:
        """PATCH the changed attributes of `existing`, or POST a new `kind` resource."""
        if existing:
            changed = {k: v for k, v in attrs.items() if existing["attributes"].get(k) != v}
            if not changed:
                print(f"{label}: up to date")
                return
            print(f"{label}: update {', '.join(changed)}")
            if not self.dry_run:
                self.asc.request("PATCH", f"/{kind}/{existing['id']}", json={"data": {
                    "type": kind, "id": existing["id"], "attributes": changed}})
        else:
            print(f"{label}: create with {', '.join(attrs)}")
            if not self.dry_run:
                self.asc.request("POST", f"/{kind}", json={"data": {
                    "type": kind, "attributes": attrs, **create}})


def prepare_version(asc: Asc, app: str, sync: Sync, locale: str) -> None:
    """Version number, build, copyright, release type, categories, age rating, review notes."""
    settings = json.loads((META / "app.json").read_text(encoding="utf-8"))
    version_string = (ROOT / "protocol" / "VERSION").read_text(encoding="utf-8").strip()
    versions = [v for v in asc.request("GET", f"/apps/{app}/appStoreVersions")["data"]
                if v["attributes"]["appStoreState"] in ("PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED",
                                                        "REJECTED", "METADATA_REJECTED")]
    if not versions:
        print("version: none in preparation")
        return
    version = versions[0]
    attrs = {"versionString": version_string, "releaseType": settings["release_type"]}
    copyright_ = text(META / locale / "copyright.txt")
    if copyright_:
        attrs["copyright"] = copyright_
    sync.upsert("appStoreVersions", version, attrs, {}, "version")
    builds = asc.request("GET", "/builds", params={
        "filter[app]": app, "filter[preReleaseVersion.version]": version_string,
        "filter[processingState]": "VALID", "sort": "-uploadedDate", "limit": 1,
        "fields[builds]": "version"})["data"]
    current = asc.request("GET", f"/appStoreVersions/{version['id']}/relationships/build")["data"]
    if builds and (not current or current["id"] != builds[0]["id"]):
        print(f"version: select build {builds[0]['attributes']['version']}")
        if not sync.dry_run:
            try:
                asc.request("PATCH", f"/appStoreVersions/{version['id']}/relationships/build",
                            json={"data": {"type": "builds", "id": builds[0]["id"]}})
            except SystemExit as exc:  # e.g. the build is not ready for the App Store yet
                print(f"version: could not select the build: {exc}")
    elif builds:
        print(f"version: build {builds[0]['attributes']['version']} selected")

    info = next(i for i in asc.request("GET", f"/apps/{app}/appInfos")["data"]
            if i["attributes"].get("appStoreState") != "READY_FOR_SALE")
    rel = asc.request("GET", f"/appInfos/{info['id']}", params={"include": "primaryCategory,secondaryCategory"})
    have = {k: (rel["data"]["relationships"].get(k, {}).get("data") or {}).get("id")
            for k in ("primaryCategory", "secondaryCategory")}
    want = {"primaryCategory": settings["primary_category"], "secondaryCategory": settings["secondary_category"]}
    if have != want:
        print(f"categories: {want['primaryCategory']}, {want['secondaryCategory']}")
        if not sync.dry_run:
            asc.request("PATCH", f"/appInfos/{info['id']}", json={"data": {
                "type": "appInfos", "id": info["id"], "relationships": {
                    k: {"data": {"type": "appCategories", "id": v}} for k, v in want.items()}}})
    else:
        print("categories: up to date")

    answers = {k: v for k, v in json.loads((META / "age_rating.json").read_text(encoding="utf-8")).items()
               if not k.startswith("_")}
    age = asc.request("GET", f"/appInfos/{info['id']}/ageRatingDeclaration")["data"]
    sync.upsert("ageRatingDeclarations", age, answers, {}, "age rating")

    notes = text(META / "review_notes.txt")
    if notes:
        existing = asc.request("GET", f"/appStoreVersions/{version['id']}/appStoreReviewDetail").get("data")
        sync.upsert("appStoreReviewDetails", existing, {"notes": notes, "demoAccountRequired": False},
                    {"relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions",
                                                                    "id": version["id"]}}}},
                    "review notes")


def store_page(asc: Asc, app: str, sync: Sync, store: Path) -> None:
    """Name, subtitle and privacy policy (app info) and the page texts of the version being prepared."""
    locale = store.name
    info_fields = fields(store, {"name": "name", "subtitle": "subtitle", "privacy_policy_url": "privacyPolicyUrl"})
    if info_fields:  # name, subtitle and privacy policy belong to the app info, not the version
        infos = [i for i in asc.request("GET", f"/apps/{app}/appInfos")["data"]
                 if i["attributes"].get("appStoreState") != "READY_FOR_SALE"]
        for info in infos[:1]:
            locs = [x for x in asc.request("GET", f"/appInfos/{info['id']}/appInfoLocalizations")["data"]
                    if x["attributes"]["locale"] == locale]
            sync.upsert("appInfoLocalizations", locs[0] if locs else None,
                        info_fields if locs else {**info_fields, "locale": locale},
                        {"relationships": {"appInfo": {"data": {"type": "appInfos", "id": info["id"]}}}},
                        f"App Store name, subtitle and privacy policy, {locale}")
    version_fields = fields(store, {"description": "description", "keywords": "keywords",
                                    "promotional_text": "promotionalText",
                                    "support_url": "supportUrl", "marketing_url": "marketingUrl"})
    if version_fields:
        versions = [v for v in asc.request("GET", f"/apps/{app}/appStoreVersions")["data"]
                    if v["attributes"]["appStoreState"] in ("PREPARE_FOR_SUBMISSION",
                                                            "DEVELOPER_REJECTED", "REJECTED",
                                                            "METADATA_REJECTED")]
        if not versions:
            print(f"App Store page {locale}: no version in preparation; nothing to update")
        for v in versions[:1]:
            locs = [x for x in asc.request(
                "GET", f"/appStoreVersions/{v['id']}/appStoreVersionLocalizations")["data"]
                if x["attributes"]["locale"] == locale]
            sync.upsert("appStoreVersionLocalizations", locs[0] if locs else None,
                        version_fields if locs else {**version_fields, "locale": locale},
                        {"relationships": {"appStoreVersion": {"data": {
                            "type": "appStoreVersions", "id": v["id"]}}}},
                        f"App Store page {locale}, version {v['attributes']['versionString']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="show what would change")
    parser.add_argument("--build", help="build number for What to Test (default: newest)")
    args = parser.parse_args()
    env = read_env()
    asc = Asc(env)
    app = env["ASC_APP_ID"]
    sync = Sync(asc, args.dry_run)
    locale = asc.request("GET", f"/apps/{app}", params={"fields[apps]": "primaryLocale"})[
        "data"]["attributes"]["primaryLocale"]
    store = META / locale

    # TestFlight: app description and What to Test
    beta = {**fields(META / "testflight", {"beta_description": "description"}),
            **fields(store, {"privacy_policy_url": "privacyPolicyUrl", "marketing_url": "marketingUrl"})}
    if beta:
        found = [x for x in asc.request("GET", f"/apps/{app}/betaAppLocalizations")["data"]
                 if x["attributes"]["locale"] == locale]
        sync.upsert("betaAppLocalizations", found[0] if found else None,
                    beta if found else {**beta, "locale": locale},
                    {"relationships": {"app": {"data": {"type": "apps", "id": app}}}},
                    "TestFlight description")
    whats_new = fields(META / "testflight", {"whats_new": "whatsNew"})
    if whats_new:
        params = {"filter[app]": app, "sort": "-uploadedDate", "limit": 1,
                  "fields[builds]": "version"}
        if args.build:
            params = {"filter[app]": app, "filter[version]": args.build, "fields[builds]": "version"}
        builds = asc.request("GET", "/builds", params=params)["data"]
        if not builds:
            raise SystemExit(f"no build {args.build or ''} found")
        build = builds[0]
        found = [x for x in asc.request("GET", f"/builds/{build['id']}/betaBuildLocalizations")["data"]
                 if x["attributes"]["locale"] == locale]
        attrs = whats_new if found else {**whats_new, "locale": locale}
        sync.upsert("betaBuildLocalizations", found[0] if found else None, attrs,
                    {"relationships": {"build": {"data": {"type": "builds", "id": build["id"]}}}},
                    f"What to Test, build {build['attributes']['version']}")

    # App Store page, one folder per language
    for folder in sorted(p for p in META.iterdir() if p.is_dir() and re.fullmatch(r"[a-z]{2}(-[A-Z]{2})?", p.name)):
        try:
            store_page(asc, app, sync, folder)
        except SystemExit as exc:  # e.g. the version is in review and cannot change
            print(f"App Store page {folder.name}: {exc}")
    prepare_version(asc, app, sync, locale)
    if args.dry_run:
        print("dry run: nothing changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
