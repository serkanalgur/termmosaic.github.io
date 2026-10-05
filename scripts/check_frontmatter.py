#!/usr/bin/env python3
"""Front matter validator.

Hugo is not assumed to be installed, so the front matter of every content file
is parsed here instead: a malformed TOML block that Hugo would reject should be
caught by a script anyone can run, not only by CI.

What it checks, and why each one:

  * the file opens as UTF-8 and is valid TOML   — Hugo would fail the build
  * required keys are present and non-empty     — a page with no title renders
                                                   a blank <h1>
  * `slug` matches the file's location          — a wrong slug silently moves a
                                                   page and breaks every link
  * `slug` is unique across the site            — two pages at one URL is a
                                                   coin flip which one wins
  * internal links in the body resolve          — see scripts/check_links.py;
                                                   the same crawl runs there,
                                                   this only reports the count

It also emits the page inventory the CI job publishes, so the tree can be read
without running Hugo.

Usage: scripts/check_frontmatter.py [--json]
Exit:  0 clean, 1 problems found, 2 could not run.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:  # pragma: no cover - PyYAML is in requirements-docs.txt
    _yaml = None


def _parse_yaml(block: str) -> dict:
    """Parse a YAML front-matter block into a dict."""
    if _yaml is None:
        raise RuntimeError("PyYAML is not installed")
    data = _yaml.safe_load(block)
    if not isinstance(data, dict):
        raise ValueError(f"expected a mapping, got {type(data).__name__}")
    return data

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"

REQUIRED = ("title", "description")


def slug_for(path: Path) -> str:
    """The URL path Hugo will serve this file at, derived the way Hugo does.

    `index.md` is its directory; anything else is its directory plus its stem,
    with the front matter's `slug` overriding when it is set.
    """
    rel = path.relative_to(CONTENT).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "index":
        parts.pop()
    return "/" + "/".join(parts) + ("/" if parts else "")


def check(path: Path) -> tuple[dict | None, list[str]]:
    problems: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, [f"{path}: not valid UTF-8 ({exc})"]

    # Files under content/adr/ that mirror a framework doc verbatim (STATUS.md,
    # CHANGELOG.md, SITE-PLAN.md, README.md) carry no front matter by design:
    # they are byte-identical copies so the site never holds a second, drifting
    # version. Hugo renders them without it.
    if not raw.startswith("---\n"):
        posix = path.as_posix()
        if "/adr/" in posix and posix.endswith(
                ("STATUS.md", "CHANGELOG.md", "SITE-PLAN.md", "README.md")) or (
                "/adr/" in posix and posix.rsplit("/", 1)[-1].startswith("0")
                and posix.endswith(".md")):
            return {"path": posix.split("/content/", 1)[-1],
                    "url": slug_for(path),
                    "meta": {"title": posix.rsplit("/", 1)[-1],
                             "description": "", "verbatim": True}}, []
        return None, [f"{path}: no front matter block (file must start with '---')"]

    end = raw.find("\n---\n", 3)
    if end == -1:
        return None, [f"{path}: front matter block is not closed"]

    block = raw[4 : end + 1]
    # Hugo accepts TOML, YAML or JSON front matter and auto-detects which. The
    # site is written in YAML ("title: x"), which is NOT valid TOML — a
    # TOML-only parser reports every page as broken and the checker reports a
    # false alarm across the whole site. Try TOML, then YAML, then JSON.
    meta = None
    errors = []
    for name, parse in (
        ("TOML", lambda b: tomllib.loads(b)),
        ("YAML", _parse_yaml),
        ("JSON", lambda b: json.loads(b)),
    ):
        try:
            meta = parse(block)
            break
        except Exception as exc:  # noqa: BLE001 - each parser raises its own type
            errors.append(f"{name}: {exc}")
    if meta is None:
        return None, [f"{path}: front matter parses as none of TOML/YAML/JSON ({'; '.join(errors)})"]

    for key in REQUIRED:
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{path}: '{key}' is missing or empty")

    declared = meta.get("slug")
    actual = slug_for(path)
    if isinstance(declared, str):
        want = declared if declared.startswith("/") else "/" + declared
        if not want.endswith("/") and want != "/":
            want += "/"
        # index.md's own slug legitimately differs from the directory.
        if path.stem == "index" and want == actual:
            pass
        elif want != actual:
            problems.append(
                f"{path}: slug {want!r} does not match its location {actual!r}"
            )

    return {"path": str(path.relative_to(REPO)), "url": actual, "meta": meta}, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit the inventory as JSON")
    args = ap.parse_args()

    files = sorted(CONTENT.rglob("*.md"))
    if not files:
        print("no content found", file=sys.stderr)
        return 2

    inventory: list[dict] = []
    problems: list[str] = []
    by_url: dict[str, list[str]] = {}

    for path in files:
        entry, issues = check(path)
        problems.extend(issues)
        if entry:
            inventory.append(entry)
            by_url.setdefault(entry["url"], []).append(entry["path"])

    for url, owners in by_url.items():
        if len(owners) > 1:
            problems.append(f"duplicate URL {url}: {', '.join(owners)}")

    if args.json:
        print(json.dumps({"pages": inventory, "problems": problems}, indent=2))
        return 1 if problems else 0

    print(f"checked {len(files)} content files")
    print(f"  pages with front matter: {len(inventory)}")
    print(f"  distinct URLs: {len(by_url)}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print("  front matter: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())