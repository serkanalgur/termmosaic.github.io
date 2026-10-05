#!/usr/bin/env bash
# Check that the verbatim framework copies under content/adr/ still match the
# framework repo. ADR files, STATUS.md, CHANGELOG.md and SITE-PLAN.md are copied
# verbatim on purpose - summarising them would create a second source of truth
# that drifts - but a verbatim copy with no check is just a second source of
# truth that nobody updates.
#
# This drifted once already: the framework's STATUS.md was corrected from 22 to
# 24 widgets and the site kept saying 22, on a page readers land on.
#
#   bash scripts/check_verbatim.sh              # verify only
#   bash scripts/check_verbatim.sh --sync       # re-copy and report what changed
#
# Set FRAMEWORK to the checkout path if it is not a sibling of this repo.
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="${FRAMEWORK:-$HOME/Projects/termmosaic}"
SYNC=0
[ "${1:-}" = "--sync" ] && SYNC=1

[ -d "$ROOT" ] || { echo "framework repo not found at $ROOT (set FRAMEWORK=...)" >&2; exit 1; }

# source-in-framework:destination-in-site
#
# Every ADR is listed, not just docs/adr/README.md. They were unguarded once and
# two of them drifted: 0001 still published the superseded golang.org/x/term pin,
# and 0008 still said a wide-glyph defect was "NOT fixed in this release" months
# after it was fixed in v0.2.0. A reader landing on either page would have been
# told something false, and nothing in CI would have said so.
#
# These copies carry Hugo front matter and drop the framework's leading H1, since
# Hugo uses the file name as the page title. So a plain byte comparison would
# always report drift. The comparison below strips front matter and a leading H1
# from both sides before diffing, and --sync re-copies then re-applies the site's
# front matter.
PAIRS=(
  "docs/STATUS.md:content/adr/STATUS.md"
  "docs/adr/README.md:content/adr/README.md"
  "CHANGELOG.md:content/adr/CHANGELOG.md"
  "docs/SITE-PLAN.md:content/adr/SITE-PLAN.md"
)

# Every ADR is discovered rather than listed. They were unguarded once and two
# drifted; they were then listed one by one, and ADR 0010 arrived while it was
# being added — so a hand-maintained list of "every ADR" is itself the thing that
# goes stale, one release at a time. A glob over the framework's own directory
# has no list to forget.
if [ -d "$ROOT/docs/adr" ]; then
  for src in "$ROOT"/docs/adr/[0-9]*.md; do
    [ -e "$src" ] || continue
    base="$(basename "$src")"
    PAIRS+=("docs/adr/$base:content/adr/$base")
  done
fi

drift=0
# Compare two markdown files ignoring Hugo front matter and a leading H1, which
# is what the site copies add. Written as a normalising filter rather than a
# diff option so --sync and the check agree by construction.
normalise() {
  awk '
    NR==1 && $0=="---" { fm=1; next }
    fm==1 && $0=="---" { fm=0; next }
    fm==1 { next }
    # Skip a leading ATX H1 and every blank line before the body proper. The
    # framework files start with the H1 and a blank line; the Hugo copies start
    # straight at the body. Applied to both sides so what remains is substance.
    !seen && /^#[[:space:]]/ { next }
    !seen && $0 ~ /^[[:space:]]*$/ { next }
    { seen=1; print }
  ' "$1"
}

for pair in "${PAIRS[@]}"; do
  src="$ROOT/${pair%%:*}"
  dst="${pair##*:}"
  name="$(basename "$src")"

  if [ ! -f "$src" ]; then
    echo "MISSING IN FRAMEWORK: $src" >&2
    drift=$((drift + 1))
    continue
  fi

  changed="$(diff <(normalise "$src") <(normalise "$dst") | grep -c '^[<>]' || true)"

  if [ "$changed" -eq 0 ]; then
    echo "  in sync: $name"
    continue
  fi

  if [ "$SYNC" = "1" ]; then
    # Re-copy the body, but keep the site's front matter: it carries the Hugo
    # title, weight and aliases that the framework file has no reason to know.
    # normalise() is the single definition of "same content", so the written file
    # is produced by exactly the transform it is compared with -- otherwise the
    # two can disagree and --sync would oscillate.
    if [ -f "$dst" ] && head -1 "$dst" | grep -q '^---$'; then
      awk 'NR==1 && $0=="---" {f=1} f {print} f && NR>1 && $0=="---" {exit}' "$dst" > "$dst.tmp"
      printf '\n' >> "$dst.tmp"
      normalise "$src" >> "$dst.tmp"
      mv "$dst.tmp" "$dst"
    else
      cp "$src" "$dst"
    fi
    echo "SYNCED:    $name ($changed lines differ)"
  else
    echo "DRIFTED:   $name ($changed lines) - $src differs from $dst" >&2
    drift=$((drift + 1))
  fi
done

if [ "$drift" -gt 0 ]; then
  echo "" >&2
  echo "$drift verbatim file(s) have drifted from the framework repo." >&2
  echo "Re-sync with: bash scripts/check_verbatim.sh --sync" >&2
  exit 1
fi

echo ""
echo "all verbatim framework copies match."