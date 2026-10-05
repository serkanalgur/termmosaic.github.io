---
title: "Responsiveness"
description: "ClampCount, Budget, Priority, MinSize — the shared arithmetic, the degenerate-size contract, and why there are no breakpoints."
weight: 27
toc: true
---

# Responsiveness

How a TermMosaic widget behaves when its rectangle shrinks. The reasoning is
[ADR 0007](/adr/0007-responsive-screens/), which is the longest decision document
in the project and the one most worth reading in full.

## The decision in one line

**Responsiveness is a budget, not a reflow.**

## There are no breakpoints and no size classes

**This is a "no", and it is one of the more argued decisions in the project.**

The reasoning: *a size class is a lossy function of two numbers and a product
decision in the wrong layer.* Concretely — what would a `Medium` class mean for a
table whose columns need 80 cells and a meter whose threshold label needs 18? A
class cannot carry that, so the class would become a set of thresholds in the
wrong place: named in the framework, owned by nobody, and duplicated in every
widget that needed a different answer.

**So each widget's threshold is a local named constant beside its own `Draw`.**
That is where the knowledge is: next to the code that has to act on it.

## What *is* shared: the arithmetic

Three things, in `geometry`, plus one optional interface:

```go
func ClampCount(n, available int) int
func Budget(regions []Region, available int) []Region
```

`geometry.Budget` distributes available rows among regions by a four-value
`Priority` scale, and `geometry.ClampCount` is the one-liner that clamps a count
to what fits. The framework shares the arithmetic; **policy stays per widget.**

### `Priority` has four values

`Required`, then three levels of optional. A region below the line is not drawn;
a `Required` region is never dropped. The four-value scale is small on purpose:
a longer scale turns "how important is this" into a tuning exercise, and tuning a
layout priority is how a layout becomes unpredictable.

### One honest caveat

**`ClampCount` and `Budget` count cells, not glyphs**, so a row budget computed
from them can be **one row optimistic** once wide characters are in play. That is
recorded rather than smoothed over — see
[Limitations](/limitations/#text-and-internationalization).

## `Minimizable`

An optional interface a widget implements if it has a smallest size at which it
can render something meaningful:

```go
type Minimizable interface {
    Widget
    MinSize() Size
}
```

**`MinSize()` includes the widget's own chrome.** A bordered `Table` with
`MinSize{20, 5}` needs 20×5 cells, not a 20×5 content area. Pinning that here is
deliberate: three authors would otherwise each decide whether their border counts,
and every caller's arithmetic would then be wrong for some subset of the catalog.

Every widget page on this site reports the value that was **called**, not parsed —
`NewTable(rect, cols).MinSize()` returns the real answer even though the
thresholds are private constants.

### The framework does nothing with it

**What to do when the available space is below a widget's `MinSize()` is the
application's decision**, because only the application knows whether losing a
table is acceptable. ADR 0007 records the rejected alternative explicitly: a
framework-owned "too small" screen. It was rejected because the framework cannot
know which of your widgets matters, and a screen that decides for you is a screen
that decides wrong.

## Degenerate sizes are a contract

> **No panic, ever. Clip, never blank.**

- A **0×0 rect is valid** and writes **zero bytes**.
- Below `MinSize()`, a widget draws its minimum layout **clipped**.
- `Draw` must be **total** for every rect, including 0×0 and 1×1.
- A resize **always repaints the whole screen**, because `buffer.Resize` discards
  the cells a partial diff would need.

The four ADR 0007 §3 tests that pin this exist as of v0.1.0:
`TestRenderAtZeroSizeWritesNothing`, `TestResizeShrinksAndRepaintsWholeRect`,
`TestResizeCoalescedToOneRepaintPerTick`, `TestRootBoundsClippedToScreen`, plus
`TestRootBoundsEntirelyOffScreenClipsToNothing`.

**Writing them found a real defect:** `Render` flushed the sink even when it wrote
nothing, breaking ADR 0007 §4's "does not call the Sink" contract for a
zero-sized screen. `Render` now flushes only when bytes went out. That is the
argument for having the tests rather than the prose.

## Drag-resize coalescing is free

An application that calls `r.Resize` on every resize event and lets
`render.Pacer` decide when to paint **already gets coalescing**. There is no
special mechanism, and no configuration to get wrong.

## The amendment: `Invalidate()` also means "drop your cache"

**This is the part most likely to cost you an afternoon.**

A widget caches column widths against `Bounds()`. The user drags the window.
`Bounds()` changes, the cache misses, all is well. Now the application sets
`Header = true`. `Bounds()` is unchanged, so **the cache still hits, and the
header never appears** — and nothing will ever produce a different rect to repair
it, because the size is not what changed.

So as of ADR 0007's 2026-10-04 amendment:

> **`Invalidate()` now also means drop every value the widget has cached.**

**For your widgets: any setter that writes a field `Draw` reads must
invalidate.** `Table.Header` is the worked example, and the framework's widgets
all obey it.

## What has *not* been observed

**No resize has ever been observed against a real terminal being dragged.** The
drag-resize costs in ADR 0007 are *derived* from existing code and from
[ADR 0002](/adr/0002-buffer-representation/) and
[ADR 0003](/adr/0003-renderer-mode/)'s measurements. ADR 0007 says so itself, and
so does [Limitations](/limitations/#layout-and-responsiveness).

Two open items from the same area:

- **The cache-audit mode is built and gates the build; its coverage is not
  total.** ADR 0007's expensive half shipped in v0.5.0 — it corrupts a widget's
  cache after `Draw` and asserts the next frame is byte-identical, and
  `widgets/cacheaudit` fails the build on a finding. It found **eight** real stale
  caches on its first run. What remains open is its reach: it audits the
  transitions it names, and several same-shaped exported raw fields are named by
  none.
- **The scripted resize sweep is not a human dragging a window.** The
  degenerate-size sweep and `examples/hello`'s grow/shrink/degenerate/recover
  golden test are real, and they are not the same thing.

## The two rules that inherit everywhere

They are non-negotiable and every widget in the catalog obeys them:

1. **A widget's available space is `Bounds()`, never `buf.Size()`.**
2. **A widget repaints its whole `Bounds()` before drawing content into it.**

Rule 2 exists because the renderer diffs and never clears, so a widget that does
not repaint its rect leaves stale cells behind after a shrink. Composing a
[`Block`](/widgets/block/) in `Background` does it for you, which is the main
reason to.

## Reading next

- [Layout and constraints](/concepts/layout/) — `Solve` and its overflow rule.
- [`KeyHint`](/widgets/keyhint/) — a widget whose degradation is a visible
  truncation, shown at 40 columns on its page.
- [Performance](/guides/performance/) — which responsiveness claims are measured
  and which are derived.
- [ADR 0007](/adr/0007-responsive-screens/) — verbatim, and the amendment.