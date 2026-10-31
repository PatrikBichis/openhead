"""Protocol tooling: validate schemas, examples and themes; generate the bundle, models and docs.

Run from the repository root:

    uv run --project python python tools/protocol.py check
    uv run --project python python tools/protocol.py generate          # write generated files
    uv run --project python python tools/protocol.py generate --check  # fail if they are stale
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocol"
SCHEMA_DIR = PROTOCOL / "schema"
EXAMPLES = PROTOCOL / "examples"
THEMES = ROOT / "face" / "themes"
BUNDLE = PROTOCOL / "dist" / "openhead.schema.json"
DOCS = PROTOCOL / "docs"
MODELS = ROOT / "python" / "src" / "openhead" / "protocol" / "models.py"
REGISTRY_PY = ROOT / "python" / "src" / "openhead" / "protocol" / "registry.py"
SWIFT_DIR = ROOT / "apps" / "ios" / "OpenHead" / "Protocol"
QUICKTYPE = "quicktype@26.0.0"
# Swift names that would shadow the standard library.
SWIFT_RENAMES = {"Error": "ProtocolError"}
# Names quicktype changes on its own (it treats "Ack" as an acronym).
QUICKTYPE_NAMES = {"Ack": "ACK"}
THEME_SCHEMA = SCHEMA_DIR / "theme.schema.json"
EXPRESSIONS_SCHEMA = SCHEMA_DIR / "expressions.schema.json"
DIALECT = "https://json-schema.org/draft/2020-12/schema"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def schema_files() -> list[Path]:
    return sorted(SCHEMA_DIR.rglob("*.json"))


def protocol_version() -> str:
    return (PROTOCOL / "VERSION").read_text(encoding="utf-8").strip()


# --- validation -------------------------------------------------------------


def registry() -> Registry:
    return Registry().with_resources(
        (p.as_uri(), Resource.from_contents(load(p), default_specification=DRAFT202012))
        for p in schema_files()
    )


def validator(reg: Registry, path: Path, fragment: str = "") -> Draft202012Validator:
    return Draft202012Validator({"$ref": path.as_uri() + fragment}, registry=reg)


def message_types() -> dict[str, Path]:
    """Map each message `type` constant to the schema file that defines it."""
    types = {}
    for path in schema_files():
        const = load(path).get("properties", {}).get("type", {}).get("const")
        if const:
            types[const] = path
    return types


def errors_of(v: Draft202012Validator, data) -> list[str]:
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(v.iter_errors(data), key=lambda e: list(map(str, e.path)))
    ]


def result_schema_for(name: str, types: dict[str, Path]) -> Path | None:
    stem = name.removesuffix(".json")
    while stem:
        if stem in types:
            return types[stem]
        stem = stem.rpartition(".")[0]
    return None


def check() -> int:
    problems: list[str] = []
    titles: dict[str, Path] = {}
    for path in schema_files():
        schema = load(path)
        if schema.get("$schema") != DIALECT:
            problems.append(f"{rel(path)}: $schema must be {DIALECT}")
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - report every schema error
            problems.append(f"{rel(path)}: invalid schema: {exc}")
        title = schema.get("title")
        if not title or not re.fullmatch(r"[A-Z][A-Za-z0-9]*", title):
            problems.append(f"{rel(path)}: needs a PascalCase title")
        elif title in titles:
            problems.append(f"{rel(path)}: title {title} also used by {rel(titles[title])}")
        else:
            titles[title] = path
    try:
        bundle()
    except ValueError as exc:
        problems.append(str(exc))

    reg = registry()
    types = message_types()
    covered: set[str] = set()
    counts = {"messages": 0, "results": 0, "invalid": 0, "themes": 0}

    for path in sorted(EXAMPLES.glob("*.json")):
        data = load(path)
        schema = types.get(data.get("type"))
        if schema is None:
            problems.append(f"{rel(path)}: unknown type {data.get('type')!r}")
            continue
        covered.add(data["type"])
        counts["messages"] += 1
        problems += [f"{rel(path)}: {e}" for e in errors_of(validator(reg, schema), data)]

    for path in sorted((EXAMPLES / "results").glob("*.json")):
        schema = result_schema_for(path.name, types)
        if schema is None or "result" not in load(schema).get("$defs", {}):
            problems.append(f"{rel(path)}: no command with a $defs/result matches the file name")
            continue
        counts["results"] += 1
        v = validator(reg, schema, "#/$defs/result")
        problems += [f"{rel(path)}: {e}" for e in errors_of(v, load(path))]

    for path in sorted((EXAMPLES / "invalid").glob("*.json")):
        data = load(path)
        schema = types.get(data.get("type"))
        counts["invalid"] += 1
        if schema and not errors_of(validator(reg, schema), data):
            problems.append(f"{rel(path)}: expected to be invalid but validates")

    for type_ in sorted(set(types) - covered):
        problems.append(f"no example in protocol/examples/ for type {type_!r}")

    theme_dirs = sorted(p.parent for p in EXAMPLES.glob("themes/*/theme.json"))
    theme_dirs += sorted(p.parent for p in THEMES.glob("*/theme.json"))
    for folder in theme_dirs:
        counts["themes"] += 1
        theme = load(folder / "theme.json")
        problems += [
            f"{rel(folder / 'theme.json')}: {e}"
            for e in errors_of(validator(reg, THEME_SCHEMA), theme)
        ]
        if theme.get("name") != folder.name:
            problems.append(f"{rel(folder / 'theme.json')}: name must equal folder {folder.name!r}")
        expr = folder / "expressions.json"
        if not expr.exists():
            problems.append(f"{rel(folder)}: missing expressions.json")
        else:
            v = validator(reg, EXPRESSIONS_SCHEMA)
            problems += [f"{rel(expr)}: {e}" for e in errors_of(v, load(expr))]
        for shape in theme.get("shapes", {}).values():
            if "image" in shape and not (folder / shape["image"]).exists():
                problems.append(f"{rel(folder)}: missing {shape['image']}")

    for p in problems:
        print(f"ERROR {p}")
    summary = ", ".join(f"{n} {k}" for k, n in counts.items())
    print(f"{len(schema_files())} schemas, {summary}: {'FAILED' if problems else 'OK'}")
    return 1 if problems else 0


# --- bundle -----------------------------------------------------------------


def pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[_\-.]", name))


def bundle() -> dict:
    """Merge all schema files into one document whose $defs are named by title.

    File roots become `$defs/<Title>`, and a file's `$defs/<name>` becomes
    `$defs/<Title><Name>`. Only refs of the form `file.json`, `file.json#/$defs/x`
    and `#/$defs/x` are allowed, which keeps the mapping unambiguous.
    """
    docs = {p.resolve(): load(p) for p in schema_files()}

    def is_defs_only(doc: dict) -> bool:
        return not ({"type", "properties", "allOf", "oneOf", "anyOf", "$ref"} & doc.keys())

    def target(ref: str, source: Path) -> str:
        path, _, fragment = ref.partition("#")
        file = (source.parent / path).resolve() if path else source
        if file not in docs:
            raise ValueError(f"{rel(source)}: $ref {ref!r} points to a missing file")
        title = docs[file]["title"]
        if fragment in ("", "/"):
            if is_defs_only(docs[file]):
                raise ValueError(f"{rel(source)}: $ref {ref!r} targets a definitions-only file")
            return f"#/$defs/{title}"
        m = re.fullmatch(r"/\$defs/([A-Za-z0-9_]+)", fragment)
        if not m or m.group(1) not in docs[file].get("$defs", {}):
            raise ValueError(f"{rel(source)}: unsupported or dangling $ref {ref!r}")
        return f"#/$defs/{title}{pascal(m.group(1))}"

    def rewrite(node, source: Path):
        if isinstance(node, dict):
            return {
                k: (target(v, source) if k == "$ref" else rewrite(v, source))
                for k, v in node.items()
            }
        if isinstance(node, list):
            return [rewrite(v, source) for v in node]
        return node

    defs: dict[str, dict] = {}
    for path, doc in docs.items():
        doc = copy.deepcopy(doc)
        local = doc.pop("$defs", {})
        doc.pop("$schema", None)
        if not is_defs_only(doc):
            defs[doc["title"]] = rewrite(doc, path)
        for name, sub in local.items():
            sub_title = doc["title"] + pascal(name)
            defs[sub_title] = {"title": sub_title, **rewrite(sub, path)}
    return {
        "$schema": DIALECT,
        "title": "OpenHeadProtocol",
        "description": f"All OpenHead protocol {protocol_version()} schemas in one document. "
        "Generated from protocol/schema by tools/protocol.py; do not edit.",
        "$defs": dict(sorted(defs.items())),
    }


# --- generation -------------------------------------------------------------


def generate_models(bundle_path: Path, out: Path) -> str:
    subprocess.run(
        [
            sys.executable, "-m", "datamodel_code_generator",
            "--input", str(bundle_path),
            "--input-file-type", "jsonschema",
            "--output", str(out),
            "--output-model-type", "pydantic_v2.BaseModel",
            "--target-python-version", "3.11",
            "--disable-timestamp",
            # Receivers ignore unknown fields so older clients survive newer devices;
            # schema validation (check) is where strictness lives.
            "--extra-fields", "ignore",
            "--use-title-as-name",
            "--collapse-root-models",
            "--use-schema-description",
            "--use-field-description",
            "--field-constraints",
            "--enum-field-as-literal", "all",
            "--use-standard-collections",
            "--use-union-operator",
            "--use-double-quotes",
            "--formatters", "black", "isort",
            "--custom-file-header",
            "# Generated from protocol/schema by tools/protocol.py. Do not edit.",
        ],
        check=True,
    )
    return out.read_text(encoding="utf-8")


def generate_registry(types: dict[str, Path]) -> str:
    lines = [
        "# Generated from protocol/schema by tools/protocol.py. Do not edit.",
        '"""Map of message `type` to its generated model."""',
        "",
        "from pydantic import BaseModel",
        "",
        "from . import models",
        "",
        f'PROTOCOL_VERSION = "{protocol_version()}"',
        "",
        "MESSAGE_TYPES: dict[str, type[BaseModel]] = {",
    ]
    for type_, path in sorted(types.items()):
        lines.append(f'    "{type_}": models.{load(path)["title"]},')
    lines.append("}")
    return "\n".join(lines) + "\n"


def generate_docs(out_dir: Path) -> None:
    from json_schema_for_humans.generate import generate_from_filename
    from json_schema_for_humans.generation_configuration import GenerationConfiguration

    config = GenerationConfiguration(
        template_name="md",
        with_footer=False,
        show_toc=False,
        examples_as_yaml=False,
    )
    for path in schema_files():
        target = out_dir / path.relative_to(SCHEMA_DIR).with_suffix(".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        generate_from_filename(str(path), str(target), config=config)

    types = message_types()
    index = [
        "# OpenHead protocol reference",
        "",
        (
            f"Protocol version {protocol_version()}. Generated from `protocol/schema` by "
            "`tools/protocol.py`; do not edit. Examples are in `protocol/examples`."
        ),
        "",
        "| Type | Schema | Description |",
        "| --- | --- | --- |",
    ]
    for type_, path in sorted(types.items()):
        doc = path.relative_to(SCHEMA_DIR).with_suffix(".md").as_posix()
        description = load(path).get("description", "").split(". ")[0].rstrip(".")
        index.append(f"| `{type_}` | [{load(path)['title']}]({doc}) | {description}. |")
    index += [
        "",
        (
            "Shared: [Envelope](envelope.md), [Command](command.md), [Common](common.md). "
            "Theme packs: [Theme](theme.schema.md), [Expressions](expressions.schema.md)."
        ),
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(index), encoding="utf-8", newline="\n")


def swift_schema(full: dict) -> dict:
    """Bundle reshaped for quicktype, which ignores `allOf` refs: inherited fields are
    copied into each type, conditionals dropped and theme/shared-only defs left out."""
    defs = full["$defs"]
    skip = ("Theme", "Expressions", "Common", "Envelope", "Command", "OpenHeadProtocol")

    def flat(name: str) -> dict:
        node = copy.deepcopy(defs[name])
        props: dict = {}
        required: list[str] = []
        for part in node.pop("allOf", []):
            src = flat(part["$ref"].rsplit("/", 1)[1]) if "$ref" in part else part
            props.update(src.get("properties", {}))
            required += src.get("required", [])
        props.update(node.get("properties", {}))
        required += node.get("required", [])
        for key in ("if", "then", "else", "oneOf", "unevaluatedProperties"):
            node.pop(key, None)
        if props:
            node["properties"] = props
            node["required"] = sorted(set(required), key=required.index)
        return node

    out = {name: flat(name) for name in defs}
    for old, new in SWIFT_RENAMES.items():
        out[new] = {**out.pop(old), "title": new}
    text = json.dumps(out)
    for old, new in SWIFT_RENAMES.items():
        text = text.replace(f'"#/$defs/{old}"', f'"#/$defs/{new}"')
    out = json.loads(text)
    roots = sorted(n for n, d in out.items() if not n.startswith(skip) and "properties" in d)
    return {
        "$schema": DIALECT,
        "title": "OpenHeadProtocol",
        "type": "object",
        "properties": {n: {"$ref": f"#/$defs/{n}"} for n in roots},
        "$defs": out,
    }, roots


def generate_swift(tmp_dir: Path) -> dict[str, str]:
    schema, roots = swift_schema(bundle())
    src = tmp_dir / "swift.schema.json"
    src.write_text(json.dumps(schema, indent=1), encoding="utf-8")
    out = tmp_dir / "Models.swift"
    subprocess.run(
        [
            "npx", "--yes", QUICKTYPE,
            "--src-lang", "schema", "--lang", "swift",
            "--top-level", "OpenHeadProtocol",
            "--struct-or-class", "struct",
            "--access-level", "public",
            "--protocol", "equatable",
            "--acronym-style", "pascal",
            "--sendable",
            "--support-linux",
            "--no-initializers",
            "-o", str(out), str(src),
        ],
        check=True,
        shell=sys.platform == "win32",
    )
    header = "// Generated from protocol/schema by tools/protocol.py (quicktype). Do not edit.\n\n"
    models = header + out.read_text(encoding="utf-8")
    for name in roots:
        name = QUICKTYPE_NAMES.get(name, name)
        if not re.search(rf"^public struct {name}\b", models, re.MULTILINE):
            raise SystemExit(f"quicktype did not emit a Swift struct named {name}")

    types = message_types()
    lines = [
        header.rstrip(),
        "",
        f'public let protocolVersion = "{protocol_version()}"',
        "",
        "/// Message `type` to its generated model.",
        "public let messageTypes: [String: any Codable.Type] = [",
    ]
    for type_, path in sorted(types.items()):
        title = load(path)["title"]
        name = QUICKTYPE_NAMES.get(title, SWIFT_RENAMES.get(title, title))
        lines.append(f'    "{type_}": {name}.self,')
    lines.append("]")
    return {"Models.swift": models, "MessageTypes.swift": "\n".join(lines) + "\n"}


def normalise(text: str) -> str:
    return text.replace("\r\n", "\n")


def sync_file(target: Path, content: str, changed: list[str], dry: bool) -> None:
    content = normalise(content)
    old = normalise(target.read_text(encoding="utf-8")) if target.exists() else None
    if old != content:
        changed.append(rel(target))
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")


def generate(dry: bool) -> int:
    changed: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        bundle_text = json.dumps(bundle(), indent=2) + "\n"
        tmp_bundle = tmp_dir / "bundle.json"
        tmp_bundle.write_text(bundle_text, encoding="utf-8")
        sync_file(BUNDLE, bundle_text, changed, dry)
        sync_file(MODELS, generate_models(tmp_bundle, tmp_dir / "models.py"), changed, dry)
        sync_file(REGISTRY_PY, generate_registry(message_types()), changed, dry)
        for name, text in generate_swift(tmp_dir).items():
            sync_file(SWIFT_DIR / name, text, changed, dry)

        docs_tmp = tmp_dir / "docs"
        generate_docs(docs_tmp)
        fresh = {p.relative_to(docs_tmp) for p in docs_tmp.rglob("*.md")}
        for relpath in sorted(fresh):
            sync_file(DOCS / relpath, (docs_tmp / relpath).read_text(encoding="utf-8"),
                      changed, dry)
        for stale in sorted(p for p in DOCS.rglob("*.md") if p.relative_to(DOCS) not in fresh):
            changed.append(rel(stale) + " (stale)")
            if not dry:
                stale.unlink()

    for c in changed:
        print(f"{'STALE' if dry else 'wrote'} {c}")
    if dry and changed:
        print("Generated files are out of date: run "
              "`uv run --project python python tools/protocol.py generate`.")
        return 1
    print("generated files up to date" if not changed else f"{len(changed)} files updated")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="validate schemas, examples and themes")
    gen = sub.add_parser("generate", help="write bundle, Python models and docs")
    gen.add_argument("--check", action="store_true", help="only report stale files")
    args = parser.parse_args()
    if args.cmd == "check":
        return check()
    return generate(dry=args.check)


if __name__ == "__main__":
    sys.exit(main())
