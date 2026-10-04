---
title: "Virtualization"
description: "The virtual/ engine behind List, Table and Tree, and what the flat-cost claim actually means."
weight: 28
toc: true
---

# Virtualization

`List`, `Table` and `Tree` share one row-virtualization engine in the `virtual/`
package. This page is about what the engine does and, more usefully, **what the
"flat cost" claim does and does not mean** — because a claim that gets quoted
without its conditions is worse than no claim.

## The measured numbers

The claim the catalog exists to back up is that **per-frame cost is flat in item
count**:

| Items | `List` | `Table` |
|---|---|---|
| 10,000 | 13,320 ns | 16,801 ns |
| 100,000 | 14,242 ns | 17,885 ns |

**Ten times the data for seven percent more time, both at zero allocations.**
These are the framework's own benchmarks in `widgets/data/bench_test.go`, and they
are also quoted in the project's README, `CHANGELOG` and `docs/STATUS.md`.

## What "flat" actually claims — and what it does not

**It claims:** the cost of drawing frame *N* does not grow with the number of
items, because only the visible rows are rendered.

**It does not claim:**

- **That mutating the data is free.** Changing an item list invalidates. Doing
  that every frame is your decision, and it is a different cost from drawing.
- **That 100,000 items is free to *hold*.** Flat per-frame cost does not change
  the memory your slice occupies.
- **That the numbers cover your scene.** They are the widgets' own benchmarks.
  Your scene's cost is your widgets' cost plus your own `Draw`.
- **That it is constant forever.** "Flat from 10 to 1,000,000" is the project's
  phrasing for the range the engine is exercised over. It is not a proof.

## How the laziness works

The engine tracks a window onto the logical row space and hands each widget the
visible slice. Two consequences worth knowing:

**Scrolling is `virtual.ScrollIntoView`, not a per-widget re-centring rule.** ADR
0007 §6 rule 2 is *clamp, do not recentre*: scrolling a selection into view moves
it the minimum distance that brings it on screen. A widget that re-centred would
make the list jump under the user's keypress.

**`Tree` renders only the visible rows of an expanded tree** — which is the same
mechanism, not a second one. A `Tree` over a filesystem you have not walked is a
tree over nothing: **laziness means only visible rows are rendered; the nodes and
the open/closed flags are yours to provide and hold.**

## Where the flat cost comes from

Two places, both of which are also the reason the diff is fast:

1. **Only visible rows are drawn.** `Draw` runs for every widget every frame
   ([ADR 0003](/adr/0003-renderer-mode/)); the engine keeps "every widget" from
   meaning "every row".
2. **Rows that did not change are skipped by the diff.** The byte-wise row
   comparison in [ADR 0002](/adr/0002-buffer-representation/) is what makes a
   scroll cheap *after* the rows are rendered: on a 200×60 scene that is 99%
   static chrome, the diff writes 141 bytes where a full repaint writes 19,979.

Point 2 is the one that is easy to miss. **Virtualization bounds the render cost;
the diff bounds the output cost.** They are different problems and both are
needed.

## `Table` keeps two horizontal offsets

Worth knowing if you work with horizontal scrolling, because it explains a
behaviour that looks like a bug:

`Table` keeps a **column index** *and* a **cell position**. The cell position is
set to a column start only when a caller asks for one. `clampColOffset`'s ceiling
is `totalW - contentW` — the content's **right-hand edge**, which is generally not
a column start.

Two reachable consequences, both pinned by tests:

- Scrolling to the end clamps onto that ceiling and leaves the column before it
  **partially visible**.
- Any resize that changes `contentW` or `totalW` **re-clamps onto it**, so the
  partial column can appear with **no scrolling key pressed at all**.

`SetSpansWindowIn`'s `skip` path is on the production path because of this — see
[Buffers and cells](/concepts/buffer/). ADR 0006's risk list had recorded it as
unreachable; the reasoning was wrong and the comment was corrected in place.

## `Pager` shares the model, not the engine

`Pager`'s scroll position is a **(line, sub-row) pair**, not a row index, because
its text wraps and a logical line occupies a variable number of screen rows.
That is a different problem from `List`'s, and the difference is documented in
`pager.go` as a design note.

## Reading next

- [`List`](/widgets/list/), [`Table`](/widgets/table/), [`Tree`](/widgets/tree/)
  — each with captures at three widths.
- [Data display](/guides/data-display/) — choosing between them.
- [Performance](/guides/performance/) — every measured number on this site, with
  what it does not cover.
- [ADR 0002](/adr/0002-buffer-representation/) and
  [ADR 0007](/adr/0007-responsive-screens/) — the two decisions behind this.