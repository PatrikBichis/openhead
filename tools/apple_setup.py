"""Create or reuse the Apple signing assets for OpenHead via the App Store Connect API.

Idempotent; safe to re-run (e.g. when the provisioning profile expires):

    uv run --project python python tools/apple_setup.py              # create what is missing
    uv run --project python python tools/apple_setup.py --github     # also set GitHub secrets

Reads `.env` (ASC_KEY_ID, ASC_ISSUER_ID, ASC_PRIVATE_KEY_PATH, IOS_BUNDLE_ID, ...).
Writes signing files to ~/.appstoreconnect/openhead/ (never into the repo) and fills
the matching paths and generated passwords into `.env`. Secret values are never printed.

The App Store Connect app record itself cannot be created through the public API;
create it in the web UI with the same bundle ID.
"""

from __future__ import annotations

import argparse
import base64
import secrets
import subprocess
import sys
import time
from pathlib import Path

import httpx
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
OUT = Path.home() / ".appstoreconnect" / "openhead"
API = "https://api.appstoreconnect.apple.com/v1"
APP_NAME = "OpenHead Robot Face"
PROFILE_NAME = "OpenHead App Store"
GH = r"C:\Program Files\GitHub CLI\gh.exe" if sys.platform == "win32" else "gh"


# --- .env -------------------------------------------------------------------


def read_env() -> dict[str, str]:
    env = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def set_env(key: str, value: str) -> None:
    """Set KEY=value in .env, keeping comments and order; append if missing."""
    lines = ENV.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.split("=", 1)[0].strip() == key and not line.lstrip().startswith("#"):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    ENV.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


# --- API --------------------------------------------------------------------


class Asc:
    def __init__(self, env: dict[str, str]):
        key = Path(env["ASC_PRIVATE_KEY_PATH"]).read_text(encoding="utf-8")
        now = int(time.time())
        token = jwt.encode(
            {"iss": env["ASC_ISSUER_ID"], "iat": now, "exp": now + 1200,
             "aud": "appstoreconnect-v1"},
            key, algorithm="ES256", headers={"kid": env["ASC_KEY_ID"], "typ": "JWT"},
        )
        self.http = httpx.Client(base_url=API, timeout=60,
                                 headers={"Authorization": f"Bearer {token}"})

    def request(self, method: str, path: str, **kwargs) -> dict:
        r = self.http.request(method, path, **kwargs)
        if r.status_code >= 400:
            detail = "; ".join(f"{e.get('code')}: {e.get('detail')}"
                               for e in r.json().get("errors", []))
            raise SystemExit(f"{method} {path} failed ({r.status_code}): {detail}")
        return r.json() if r.content else {}


def ensure_bundle_id(asc: Asc, identifier: str) -> tuple[str, str]:
    found = asc.request("GET", "/bundleIds", params={"filter[identifier]": identifier})["data"]
    found = [b for b in found if b["attributes"]["identifier"] == identifier]
    if found:
        print(f"bundle ID {identifier}: exists ({found[0]['id']})")
        return found[0]["id"], found[0]["attributes"]["seedId"]
    data = asc.request("POST", "/bundleIds", json={"data": {"type": "bundleIds", "attributes": {
        "identifier": identifier, "name": APP_NAME, "platform": "IOS"}}})["data"]
    print(f"bundle ID {identifier}: created ({data['id']})")
    return data["id"], data["attributes"]["seedId"]


def ensure_certificate(asc: Asc, env: dict[str, str]) -> str:
    """Reuse the certificate recorded in .env if it is still valid, else create one."""
    cert_id = env.get("APPLE_DIST_CERT_ID", "")
    p12_path = Path(env.get("APPLE_DIST_CERT_P12_PATH") or OUT / "dist.p12")
    if cert_id and p12_path.exists():
        r = asc.http.get(f"/certificates/{cert_id}")
        if r.status_code == 200:
            print(f"certificate: reusing {cert_id}, expires "
                  f"{r.json()['data']['attributes']['expirationDate'][:10]}")
            return cert_id

    OUT.mkdir(parents=True, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    csr = (x509.CertificateSigningRequestBuilder()
           .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "OpenHead CI")]))
           .sign(key, hashes.SHA256()))
    data = asc.request("POST", "/certificates", json={"data": {"type": "certificates", "attributes": {
        "certificateType": "DISTRIBUTION",
        "csrContent": csr.public_bytes(serialization.Encoding.PEM).decode()}}})["data"]
    cert = x509.load_der_x509_certificate(base64.b64decode(data["attributes"]["certificateContent"]))

    password = secrets.token_urlsafe(24)
    # 3DES/SHA1 PKCS#12 so macOS `security import` on CI runners accepts it.
    encryption = (serialization.PrivateFormat.PKCS12.encryption_builder()
                  .kdf_rounds(50000)
                  .key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
                  .hmac_hash(hashes.SHA1())
                  .build(password.encode()))
    p12 = pkcs12.serialize_key_and_certificates(b"OpenHead Apple Distribution", key, cert,
                                                None, encryption)
    (OUT / "dist.key.pem").write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode())))
    (OUT / "dist.cer").write_bytes(cert.public_bytes(serialization.Encoding.DER))
    p12_path = OUT / "dist.p12"
    p12_path.write_bytes(p12)
    set_env("APPLE_DIST_CERT_ID", data["id"])
    set_env("APPLE_DIST_CERT_P12_PATH", str(p12_path))
    set_env("APPLE_DIST_CERT_PASSWORD", password)
    print(f"certificate: created {data['id']} ({data['attributes']['name']}), "
          f"expires {data['attributes']['expirationDate'][:10]}")
    return data["id"]


def ensure_profile(asc: Asc, bundle_pk: str, cert_id: str) -> Path:
    path = OUT / "OpenHead_AppStore.mobileprovision"
    existing = asc.request("GET", "/profiles", params={"filter[name]": PROFILE_NAME,
                                                       "include": "certificates"})
    for profile in existing["data"]:
        certs = {c["id"] for c in profile["relationships"]["certificates"].get("data", [])}
        if profile["attributes"]["profileState"] == "ACTIVE" and cert_id in certs:
            path.write_bytes(base64.b64decode(profile["attributes"]["profileContent"]))
            print(f"profile: reusing {profile['id']}, expires "
                  f"{profile['attributes']['expirationDate'][:10]}")
            return path
        asc.request("DELETE", f"/profiles/{profile['id']}")
        print(f"profile: deleted stale {profile['id']}")
    data = asc.request("POST", "/profiles", json={"data": {
        "type": "profiles",
        "attributes": {"name": PROFILE_NAME, "profileType": "IOS_APP_STORE"},
        "relationships": {
            "bundleId": {"data": {"type": "bundleIds", "id": bundle_pk}},
            "certificates": {"data": [{"type": "certificates", "id": cert_id}]},
        }}})["data"]
    path.write_bytes(base64.b64decode(data["attributes"]["profileContent"]))
    print(f"profile: created {data['id']}, expires {data['attributes']['expirationDate'][:10]}")
    return path


def find_app(asc: Asc, identifier: str) -> str | None:
    apps = asc.request("GET", "/apps", params={"filter[bundleId]": identifier})["data"]
    return apps[0]["id"] if apps else None


# --- GitHub -----------------------------------------------------------------


def set_github(env: dict[str, str]) -> None:
    def gh(*args: str, stdin: str | None = None) -> None:
        subprocess.run([GH, *args], input=stdin, text=True, check=True,
                       stdout=subprocess.DEVNULL)

    def b64(path: str) -> str:
        return base64.b64encode(Path(path).read_bytes()).decode()

    secret_values = {
        "APPLE_DIST_CERT_P12_B64": b64(env["APPLE_DIST_CERT_P12_PATH"]),
        "APPLE_DIST_CERT_PASSWORD": env["APPLE_DIST_CERT_PASSWORD"],
        "APPLE_PROVISIONING_PROFILE_B64": b64(env["APPLE_PROVISIONING_PROFILE_PATH"]),
        "ASC_KEY_ID": env["ASC_KEY_ID"],
        "ASC_ISSUER_ID": env["ASC_ISSUER_ID"],
        "ASC_PRIVATE_KEY": Path(env["ASC_PRIVATE_KEY_PATH"]).read_text(encoding="utf-8"),
        "KEYCHAIN_PASSWORD": env["KEYCHAIN_PASSWORD"],
    }
    for name, value in secret_values.items():
        gh("secret", "set", name, stdin=value)
        print(f"github secret {name}: set")
    for name in ("APPLE_TEAM_ID", "IOS_BUNDLE_ID", "IOS_SCHEME"):
        gh("variable", "set", name, "--body", env[name])
        print(f"github variable {name}: {env[name]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--github", action="store_true", help="also set GitHub secrets/variables")
    args = parser.parse_args()

    env = read_env()
    for key in ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_PRIVATE_KEY_PATH", "IOS_BUNDLE_ID"):
        if not env.get(key):
            raise SystemExit(f".env: {key} is empty")
    asc = Asc(env)

    bundle_pk, team_id = ensure_bundle_id(asc, env["IOS_BUNDLE_ID"])
    if env.get("APPLE_TEAM_ID") != team_id:
        set_env("APPLE_TEAM_ID", team_id)
    cert_id = ensure_certificate(asc, read_env())
    profile = ensure_profile(asc, bundle_pk, cert_id)
    set_env("APPLE_PROVISIONING_PROFILE_PATH", str(profile))
    if not read_env().get("KEYCHAIN_PASSWORD"):
        set_env("KEYCHAIN_PASSWORD", secrets.token_urlsafe(24))

    app_id = find_app(asc, env["IOS_BUNDLE_ID"])
    if app_id:
        print(f"app record: exists ({app_id})")
    else:
        print(f"app record: missing - create it in App Store Connect (My Apps > + > New App) "
              f"with name '{APP_NAME}' and bundle ID {env['IOS_BUNDLE_ID']}")

    if args.github:
        set_github(read_env())
    return 0


if __name__ == "__main__":
    sys.exit(main())
