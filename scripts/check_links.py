#!/usr/bin/env python3
"""Link checker for the built site.

A docs site with broken links is worse than no site, so this walks the rendered
HTML in public/ and resolves every internal href against the set of URLs Hugo
actually produced. Nothing is guessed from the content tree: a link is only
"good" if its target exists in the build output.

Four classes of link, and what happens to each:

  internal page   /widgets/gauge/            resolved against the built URL set
  internal anchor /limitations/#foo          page must exist AND carry that id
  capture asset   /captures/gauge.html       must exist as a published file
  fragment-only   #foo                      must exist as an id on this page

External http(s) links are counted and reported but not fetched: a docs site
must not fail its build because someone else's server is down, and the count is
printed so a reviewer can see how many there are.

Anchors are checked against the *rendered* HTML, so a heading whose auto-generated
id changed is caught here rather than by a reader.

Usage: scripts/check_links.py [--public DIR] [--external] [--json]
Exit:  0 no broken internal links, 1 broken links found, 2 no build to check.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO = Path(__file__).resolve().parent.parent

# Hugo emits ids on headings as <h2 id="...">, and Pagefind does not add any.
ID_ATTR = re.compile(r'\bid="([^"]+)"')
HREF = re.compile(r'href="([^"]*)"')


class PageParser(HTMLParser):
    """Collects every href and every id on a page."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name == "href":
                self.hrefs.append(html.unescape(value))
            elif name == "id":
                self.ids.add(value)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser


def url_for(path: Path, public: Path) -> str:
    """The URL a browser would use to fetch this file.

    Directory indexes are served at their directory, but any other .html file is
    served at its own path with the extension. That distinction matters here:
    static/captures/*.html are standalone capture documents that are reachable at
    both /captures/gauge.html and (because some terminals and file servers guess)
    /captures/gauge/, and a link checker that only knows the directory form will
    report every internal link in them as broken.
    """
    rel = path.relative_to(public)
    parts = list(rel.parts)
    if parts and parts[-1] == "index.html":
        parts.pop()
        return "/" + "/".join(parts) + "/" if parts else "/"
    return "/" + "/".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", default="public")
    ap.add_argument("--external", action="store_true", help="also report external links")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    public = (REPO / args.public).resolve()
    if not public.is_dir():
        print(f"no build output at {public}; run hugo first", file=sys.stderr)
        return 2

    html_files = sorted(public.rglob("*.html"))
    if not html_files:
        print(f"no HTML in {public}; run hugo first", file=sys.stderr)
        return 2

    pages: dict[str, Path] = {}
    ids: dict[str, set[str]] = {}
    parsers: dict[str, PageParser] = {}

    for path in html_files:
        url = url_for(path, public)
        pages[url] = path
        parser = parse(path)
        parsers[url] = parser
        ids[url] = parser.ids

    # A published non-HTML file is a valid target too (captures, css, sitemap).
    assets = {
        "/" + str(p.relative_to(public)).replace("\\", "/")
        for p in public.rglob("*")
        if p.is_file()
    }

    internal = 0
    external: set[str] = set()
    broken: list[str] = []

    for url, parser in parsers.items():
        for href in parser.hrefs:
            if not href or href.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue
            if href.startswith(("http://", "https://", "//")):
                external.add(href)
                continue
            if href.startswith("#"):
                anchor = unquote(href[1:])
                if anchor and anchor not in ids[url]:
                    broken.append(f"{url} → {href}  (no such id on this page)")
                continue

            parsed = urlparse(href)
            target = unquote(parsed.path)
            if not target:
                continue
            if not target.startswith("/"):
                target = url.rsplit("/", 1)[0] + "/" + target if url != "/" else "/" + target
            internal += 1

            # A directory URL resolves to its index.html; that file already
            # registered the URL above, so a plain membership test is enough.
            if target in pages or target in assets or target.rstrip("/") in assets:
                anchor = unquote(parsed.fragment)
                if anchor and target in ids and anchor not in ids[target]:
                    broken.append(f"{url} → {href}  (no such id on {target})")
                continue

            # The directory form of a .html file: /captures/gauge.html is also
            # reachable as /captures/gauge/, so accept it rather than reporting
            # a false positive against the standalone capture documents.
            if target.endswith("/") and target[:-1] in pages:
                continue

            broken.append(f"{url} → {href}  (no such page or file)")

    result = {
        "pages": len(pages),
        "internal_links": internal,
        "external_links": len(external),
        "broken": broken,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if broken else 0

    print(f"pages built:              {len(pages)}")
    print(f"internal links checked:   {internal}")
    print(f"external links (not fetched): {len(external)}")
    print(f"broken internal links:    {len(broken)}")
    if args.external:
        for url in sorted(external):
            print(f"  external: {url}")
    if broken:
        print("\nbroken:")
        for b in sorted(set(broken)):
            print(f"  {b}")
        return 1
    print("\nall internal links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())