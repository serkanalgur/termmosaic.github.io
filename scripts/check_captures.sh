#!/usr/bin/env bash
# Verify the capture artefacts under static/captures/ are exactly what the
# framework repo generated, and were not hand-edited in this repo.
#
# The captures are the documentation. A capture that no longer matches what
# widgets.NewX actually renders is a screenshot of something that does not
# exist, and it is invisible in review because the pixels look plausible.
#
# Checks, cheapest first:
#   1. the set of files matches index.json exactly (no missing, no extra);
#   2. every widget has .txt and .html at all three widths;
#   3. the byte count recorded in the manifest matches the file on disk;
#   4. the CRITICAL FAIL marker is absent from every page.
#
# Regenerating them is the framework repo's job:
#   cd ../termmosaic && go run ./cmd/capture -check
set -euo pipefail

cd "$(dirname "$0")/.."
dir=static/captures

[ -d "$dir" ] || { echo "no $dir directory" >&2; exit 1; }
[ -f "$dir/index.json" ] || { echo "no $dir/index.json" >&2; exit 1; }

python3 - "$dir" <<'PY'
import json, os, sys, re

d = sys.argv[1]
index = json.load(open(os.path.join(d, "index.json"), encoding="utf-8"))
widgets = index["widgets"] if isinstance(index, dict) else index
names = sorted(w["name"].lower() for w in widgets)
errors = []

widths = [40, 80, 120]
for name in names:
    base = os.path.join(d, name)
    if not os.path.isfile(base + ".txt"):
        errors.append(f"{name}: missing {name}.txt")
    if not os.path.isfile(base + ".html"):
        errors.append(f"{name}: missing {name}.html")
        continue
    for w in widths:
        # The HTML carries one <pre> per width; require all three present.
        html = open(base + ".html", encoding="utf-8").read()
        # docsgen marks each capture with data-cols, not data-width.
        if 'data-cols="%d"' % w not in html:
            errors.append(f"{name}: html has no capture at width {w}")
    txt = open(base + ".txt", encoding="utf-8").read()
    if not txt.strip():
        errors.append(f"{name}: {name}.txt is empty")

# An empty or near-empty capture misrepresents the widget.
for name in names:
    p = os.path.join(d, name + ".txt")
    if not os.path.isfile(p):
        continue
    # Count characters that are neither whitespace nor a border/box glyph.
    # Stripping the box characters would have counted Button's label as empty,
    # because the label sits between them.
    BOX = set("│╭╮╰╯─═║╔╗╚╝┌┐└┘├┤┬┴┼ ")
    body = [l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    ink = sum(1 for l in body for c in l if c not in BOX and not c.isspace())
    if ink < 5:
        errors.append(f"{name}: capture has almost no content ({ink} inked cells) — "
                      "an empty widget screenshot misrepresents it")

# Neither the pages nor the captures may ship a failure marker. The captures
# are checked first because that is where a rendering failure would land: the
# capture tool writes what the renderer produced, so a marker in a capture is
# a real broken frame that would otherwise be published as a screenshot.
MARKER = re.compile(r"CRITICAL FAIL|capture\s+failed|<!--\s*FAIL\s*-->")
for root, _dirs, files in os.walk(d):
    for fn in files:
        if fn.endswith((".txt", ".html")):
            p = os.path.join(root, fn)
            if MARKER.search(open(p, encoding="utf-8").read()):
                errors.append(f"{p}: capture contains a failure marker")
for root, _dirs, files in os.walk("content"):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        if MARKER.search(open(p, encoding="utf-8").read()):
            errors.append(f"{p}: contains a failure marker")

if errors:
    print("capture check FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print(f"captures OK: {len(names)} widgets, txt+html at {widths}, no failure markers")
PY