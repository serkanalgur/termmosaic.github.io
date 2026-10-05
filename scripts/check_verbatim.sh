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
PAIRS=(
  "docs/STATUS.md:content/adr/STATUS.md"
  "docs/adr/README.md:content/adr/README.md"
  "CHANGELOG.md:content/adr/CHANGELOG.md"
  "docs/SITE-PLAN.md:content/adr/SITE-PLAN.md"
)

drift=0
for pair in "${PAIRS[@]}"; do
  src="$ROOT/${pair%%:*}"
  dst="${pair##*:}"
  name="$(basename "$src")"

  if [ ! -f "$src" ]; then
    echo "MISSING IN FRAMEWORK: $src" >&2
    drift=$((drift + 1))
    continue
  fi

  if diff -q "$src" "$dst" >/dev/null 2>&1; then
    echo "  in sync: $name"
    continue
  fi

  if [ "$SYNC" = "1" ]; then
    changed="$(diff "$src" "$dst" | grep -c '^[<>]' || true)"
    cp "$src" "$dst"
    echo "SYNCED:    $name ($changed lines differ)"
  else
    changed="$(diff "$src" "$dst" | grep -c '^[<>]' || true)"
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