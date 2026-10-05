---
title: "Renderer and diff"
description: "Hybrid renderer mode, dirty rectangles, the two-tier diff, and frame pacing."
weight: 21
toc: true
---

# Renderer and diff

What happens between your `Draw` and the bytes on the screen, and why each of the
three stages exists. The reasoning is [ADR 0003](/adr/0003-renderer-mode/) (mode)
and [ADR 0002](/adr/0002-buffer-representation/) (the diff and its measurement).

## Hybrid mode: retained tree, draw on demand

**"Hybrid" means exactly one thing: you keep the widget tree, and the renderer
asks widgets to describe themselves every frame.** It is not a reconciler and it
is not an Elm loop. Three things it deliberately is not:

- **No reconciler.** Nothing diffs your tree against a previous tree. You build
  the tree; the renderer draws it.
- **No virtual tree.** Your widgets are the widgets.
- **No incremental-draw interface.** `Draw` is not "draw the changed part". It is
  "draw yourself".

`Widget` is four methods and it has not changed across all ten architecture
decisions:

```go
type Widget interface {
    Bounds() Rect
    Draw(buf *buffer.Buffer)
    Invalidate()
    Handle(Event) bool
}
```

### Why not require incremental drawing

The reasoning, and it is the load-bearing part of ADR 0003: **requiring widget
authors to implement correct incremental invalidation is a discipline Go cannot
enforce.** There is no way to make a compiler reject a widget that forgets to
invalidate, and a widget that silently fails to invalidate is the worst class of
bug a TUI can have — the screen shows stale content and nothing anywhere says why.

So the framework takes the opposite bet: redraw everything, make redrawing
everything cheap, and let the diff absorb it.

### The trade, stated plainly

`Draw` runs for **every widget, every frame**, and is expected to be cheap and
idempotent — writing the same state twice must produce the same cells. The
committed measurement is **~81 µs for 12,000 cells**.

**There is no lever to pull if that ever stops being cheap.** That is the
accepted cost, recorded in ADR 0003 and in `widget.go`: the dirty-rectangle
accumulator is the seam an incremental API would attach to, when that day comes.
Nothing is built for that day.

## Dirty rectangles

`Invalidate()` marks a rectangle dirty. The renderer accumulates those
rectangles and uses them for two things: to skip work, and to decide what to
compare.

`Invalidate()` is safe to call from any goroutine — the buffer's dirty
accumulator provides that — and it means **two** things as of ADR 0007's 2026-10-04
amendment:

1. Mark `Bounds()` dirty.
2. **Drop every value the widget has cached.**

That second half is not a formality. A widget that caches column widths against
`Bounds()` and is then handed `Header = true` renders the old layout
*permanently*: no rect will ever change again, so nothing will produce the
different layout to repair it. **Any setter that writes a field `Draw` reads must
invalidate.** This is the sharpest edge in the framework and it applies to your
widgets as much as the catalog's.

## The two-tier diff

This is where the numbers come from, and they are the only performance claims
this site makes.

**Tier 1 — row skip.** For each dirty row, compare the row's bytes against the
previous frame's. Unchanged, skip the whole row. This is one wide `memcmp`.

**Tier 2 — per cell.** Within a row that differs, compare cell by cell and emit
only the cells that changed.

The measurement that justified AoS over SoA, and then the whole architecture,
on a **200×60 scene that is 99% static chrome**:

| | |
|---|---|
| Diff output | **141 bytes** |
| Full repaint | **19,979 bytes** |
| Reduction | **~141×** |
| Cost | **~7,133 ns/op** |
| Allocations | **0 allocs/op** |

A frame in which nothing is dirty **writes zero bytes and does not call the sink
at all** — so an idle application costs nothing rather than burning CPU at the
frame rate. Writing the ADR 0007 §3 tests found a real defect in exactly this
area: `Render` used to flush the sink even when it wrote nothing, and it now
flushes only when bytes went out.

### Why the cell is 16 bytes and why that is load-bearing

`Cell` is `Ch rune`, `FG Colour`, `BG Colour`, `Attr Attr`, `flags` — **exactly
16 bytes, padding-free**. The byte-wise row comparison requires that, so a
padding byte would silently double the memory traffic of tier 1.

**But padding-free is only half the condition.** ADR 0002's 2026-10-04 amendment
added the other half: the compared range must also be **contiguous**. A
`SubBuffer` returning a tightly packed slice satisfied the first and violated the
second. The structural fix is `Buffer.stride`, and ADR 0006 makes the rule
enforceable by type — see [Buffers and cells](/concepts/buffer/).

The OpenTUI comparison is worth stating because it is the kind of finding that
sounds like a contradiction until you check it: **OpenTUI's struct-of-arrays
advantage is a Zig `mem.eql` advantage and does not transfer to Go.** Packed AoS
row-skip *ties* with SoA (5,373 vs 5,128 ns/op) and is 4.4× *faster* when every
row is dirty (147.2 vs 636.7 ns/op), because it is one wide memcmp instead of
four.

## Frame pacing

`render.Pacer` decides when a frame is actually painted. An application that
calls `Resize` on every resize event and lets the pacer decide gets drag-resize
coalescing **for free** — which is why ADR 0007's resize story needs no special
mechanism.

The budget is **30–60 fps**. **`Pacer` is invisible in any capture on this site**,
which is one of the things [Limitations](/limitations/) says a picture cannot
show.

## The resize path

The order matters and ADR 0007 §5 states it:

```go
case termmosaic.EventResize:
    w, h = ev.Size.W, ev.Size.H
    root.bounds = rootBounds(w, h)   // 1. recompute the tree's rectangles
    r.Resize(w, h)                   // 2. resize the renderer
```

**Nothing goes between those two steps.** `Renderer.Resize` never draws, so the
whole interval is available to recompute bounds, and `Resize` already forces a
full repaint — because `buffer.Resize` discards the cells a partial diff would
need. The `InvalidateAll()` that used to sit there was redundant.

## Degenerate sizes are a contract

**No panic, ever. Clip, never blank.** Concretely:

- A **0×0 rect is valid** and writes zero bytes.
- Below `MinSize()`, a widget draws its minimum layout **clipped**.
- `Draw` must be **total** for every rect, including 0×0 and 1×1.
- The root is clipped to the screen, so a root entirely off screen writes
  nothing.

The framework's widgets are held to this by tests. **Yours are your
responsibility**, and it is the most common way a widget crashes on a resize.

## Read next

- [Buffers and cells](/concepts/buffer/) — the 16-byte `Cell` and its accessors.
- [Responsiveness](/concepts/responsiveness/) — `MinSize`, `ClampCount`, `Budget`.
- [ADR 0003](/adr/0003-renderer-mode/) — the full reasoning, verbatim.
- [ADR 0002](/adr/0002-buffer-representation/) — the diff, the benchmark, and the
  amendment that corrected a half-stated precondition.